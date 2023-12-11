import argparse
import logging
from typing import Optional, List

import pandas as pd
from matplotlib import pyplot as plt

from core.src.model.column_name import SubmissionColumns
from core.src.utils.df_utils import read_df
from jba.src.models.edu_columns import EduColumnName
from jba.src.plots.util import prepare_task_df_for_plots, make_plot_pretty, plot_name

logger = logging.getLogger(__name__)


MIN_STATS_COLUMN = 'min'
MAX_STATS_COLUMN = 'max'
MEDIAN_STATS_COLUMN = 'median'
MEAN_STATS_COLUMNS = 'mean'


def _count_duplicates_submissions(group: pd.DataFrame) -> List[int]:
    duplicate_submissions = []
    number_of_duplicates = 0
    for first_submission, second_submission in zip(group.itertuples(), group.shift(-1).dropna(how='all').itertuples()):
        left_snippets = getattr(first_submission, EduColumnName.CODE_SNIPPETS.value)
        right_snippets = getattr(second_submission, EduColumnName.CODE_SNIPPETS.value)

        if left_snippets == right_snippets:
            number_of_duplicates += 1
        elif number_of_duplicates != 0:
            duplicate_submissions.append(number_of_duplicates)
            number_of_duplicates = 0

    if number_of_duplicates != 0:
        duplicate_submissions.append(number_of_duplicates)

    if duplicate_submissions:
        logger.info(f'{group.name}: {duplicate_submissions}')

    return duplicate_submissions


def _compute_stats(task_id: int, course_data_df: pd.DataFrame) -> pd.Series:
    number_of_duplicates = (
        course_data_df[course_data_df[EduColumnName.TASK_ID.value] == task_id]
        .groupby(SubmissionColumns.GROUP.value)
        .apply(lambda group: max(_count_duplicates_submissions(group), default=0))
    )

    if number_of_duplicates.empty:
        logger.warning(f'There are no submissions for task#{task_id}')
        return pd.Series(
            {
                MIN_STATS_COLUMN: 0,
                MAX_STATS_COLUMN: 0,
                MEAN_STATS_COLUMNS: 0,
                MEDIAN_STATS_COLUMN: 0,
            }
        )

    return pd.Series(
        {
            MIN_STATS_COLUMN: number_of_duplicates.min(),
            MAX_STATS_COLUMN: number_of_duplicates.max(),
            MEAN_STATS_COLUMNS: number_of_duplicates.mean(),
            MEDIAN_STATS_COLUMN: number_of_duplicates.median(),
        }
    )


def plot_task_duplicates(
    course_data_df: pd.DataFrame,
    all_tasks_data_df: pd.DataFrame,
    course_name: Optional[str] = None,
):
    tasks_df = prepare_task_df_for_plots(course_data_df, all_tasks_data_df)

    stats = pd.concat(
        [
            tasks_df,
            tasks_df.apply(lambda row: _compute_stats(row[EduColumnName.TASK_ID.value], course_data_df), axis=1),
        ],
        axis=1,
    ).fillna(0)

    fig, ax = plt.subplots(dpi=300)

    stats.plot(kind='line', x=EduColumnName.TASK_NAME.value, y=MEDIAN_STATS_COLUMN, color='gray', ax=ax, style=['--'])
    stats.plot(kind='line', x=EduColumnName.TASK_NAME.value, y=MEAN_STATS_COLUMNS, color='black', ax=ax, style=[':'])
    stats.plot(kind='line', x=EduColumnName.TASK_NAME.value, y=MIN_STATS_COLUMN, color='blue', ax=ax)
    stats.plot(kind='line', x=EduColumnName.TASK_NAME.value, y=MAX_STATS_COLUMN, color='red', ax=ax)
    make_plot_pretty(ax, tasks_df, plot_name('number of duplicates', course_name), "number of duplicates")

    return fig


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        'preprocessed_course_data_path',
        type=str,
        help='Path to .csv file with preprocessed course data.',
    )
    parser.add_argument('course_structure_path', type=str, help='Path to .csv with the course structure.')
    parser.add_argument('--course-name', type=str, help='Name of the course.')


def main():
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')  # noqa: WPS323

    args = parser.parse_args()

    course_data = read_df(args.preprocessed_course_data_path)
    tasks_data_df = read_df(args.course_structure_path)

    plot_task_duplicates(course_data, tasks_data_df, args.course_name)
    plt.show()


if __name__ == '__main__':
    main()
