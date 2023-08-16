import argparse
from functools import partial
from typing import Optional, List

import pandas as pd
from matplotlib import pyplot as plt

from core.src.model.column_name import SubmissionColumns
from core.src.utils.df_utils import read_df
from jba.src.models.edu_columns import EduColumnName, EduTaskType
from jba.src.plots.util import prepare_task_df_for_plots, make_plot_pretty, plot_name


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

    return duplicate_submissions


def plot_task_duplicates(
    course_data_df: pd.DataFrame,
    all_tasks_data_df: pd.DataFrame,
    course_name: Optional[str] = None,
):
    edu_data_df = course_data_df[course_data_df[EduColumnName.TASK_TYPE.value] == EduTaskType.EDU.value]

    duplicate_submissions_column = 'duplicate_submissions'

    duplicates_by_group = (
        edu_data_df.groupby(SubmissionColumns.GROUP.value)
        .apply(_count_duplicates_submissions)
        .rename(duplicate_submissions_column)
    )

    task_by_group = (
        edu_data_df.groupby(SubmissionColumns.GROUP.value)
        .apply(lambda row: row[EduColumnName.TASK_NAME.value].iloc[0])
        .rename(EduColumnName.TASK_NAME.value)
    )

    duplicate_submissions_df = pd.concat([duplicates_by_group, task_by_group], axis=1).reset_index()

    min_stats_column = 'min'
    max_stats_column = 'max'
    median_stats_column = 'median'
    mean_stats_column = 'mean'

    min_stats = (
        duplicate_submissions_df.groupby(EduColumnName.TASK_NAME.value)
        .apply(lambda df: df[duplicate_submissions_column].apply(partial(max, default=0)).min())
        .rename(min_stats_column)
    )

    max_stats = (
        duplicate_submissions_df.groupby(EduColumnName.TASK_NAME.value)
        .apply(lambda df: df[duplicate_submissions_column].apply(partial(max, default=0)).max())
        .rename(max_stats_column)
    )

    median_stats = (
        duplicate_submissions_df.groupby(EduColumnName.TASK_NAME.value)
        .apply(lambda df: df[duplicate_submissions_column].apply(partial(max, default=0)).median())
        .rename(median_stats_column)
    )

    mean_stats = (
        duplicate_submissions_df.groupby(EduColumnName.TASK_NAME.value)
        .apply(lambda df: df[duplicate_submissions_column].apply(partial(max, default=0)).mean())
        .rename(mean_stats_column)
    )

    stats = pd.concat([min_stats, max_stats, median_stats, mean_stats], axis=1).reset_index()

    plt.figure(dpi=300)

    ax = plt.gca()
    stats.plot(kind='line', x=EduColumnName.TASK_NAME.value, y=median_stats_column, color='gray', ax=ax, style=['--'])
    stats.plot(kind='line', x=EduColumnName.TASK_NAME.value, y=mean_stats_column, color='black', ax=ax, style=[':'])
    stats.plot(kind='line', x=EduColumnName.TASK_NAME.value, y=min_stats_column, color='blue', ax=ax)
    stats.plot(kind='line', x=EduColumnName.TASK_NAME.value, y=max_stats_column, color='red', ax=ax)

    tasks_df = prepare_task_df_for_plots(course_data_df, all_tasks_data_df)
    make_plot_pretty(ax, tasks_df, plot_name('number of duplicates', course_name), "number of duplicates")

    plt.show()


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

    args = parser.parse_args()

    course_data = read_df(args.preprocessed_course_data_path)
    tasks_data_df = read_df(args.course_structure_path)
    plot_task_duplicates(course_data, tasks_data_df, args.course_name)


if __name__ == '__main__':
    main()
