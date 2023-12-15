import argparse
import sys
from typing import Optional, Dict, Tuple

import matplotlib.pyplot as plt
import pandas as pd

from core.src.utils.df_utils import read_df
from jba.src.models.edu_columns import EduColumnName
from jba.src.plots.task_stat import TaskStat, calculate_tasks_stat
from jba.src.plots.util import prepare_task_df_for_plots, make_plot_pretty, plot_name


MEDIAN_COLUMN = 'median'
MIN_COLUMN = 'min'
MAX_COLUMN = 'max'


def _calculate_median(tasks_stat: Dict[int, TaskStat], task_id: int) -> int:
    stats = tasks_stat.get(task_id)
    if stats is None:
        return 0

    return stats.median_attempts


def _calculate_min(tasks_stat: Dict[int, TaskStat], task_id: int) -> int:
    stats = tasks_stat.get(task_id)
    if stats is None:
        return 0

    return stats.min_attempts


def _calculate_max(tasks_stat: Dict[int, TaskStat], task_id: int) -> int:
    stats = tasks_stat.get(task_id)
    if stats is None:
        return 0

    return stats.max_attempts


def calculate_attempt_stats(course_data_df: pd.DataFrame, all_tasks_data_df: pd.DataFrame) -> pd.DataFrame:
    tasks_stat = calculate_tasks_stat(course_data_df)
    tasks_df = prepare_task_df_for_plots(course_data_df, all_tasks_data_df)

    tasks_df[MEDIAN_COLUMN] = tasks_df.apply(
        lambda row: _calculate_median(tasks_stat, row[EduColumnName.TASK_ID.value]),
        axis=1,
    )
    tasks_df[MIN_COLUMN] = tasks_df.apply(
        lambda row: _calculate_min(tasks_stat, row[EduColumnName.TASK_ID.value]),
        axis=1,
    )
    tasks_df[MAX_COLUMN] = tasks_df.apply(
        lambda row: _calculate_max(tasks_stat, row[EduColumnName.TASK_ID.value]),
        axis=1,
    )

    return tasks_df


def plot_task_attempts(stats: pd.DataFrame, course_name: Optional[str] = None) -> Tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(dpi=300)

    stats.plot(kind='line', x=EduColumnName.TASK_NAME.value, y=MEDIAN_COLUMN, color='black', ax=ax)
    stats.plot(kind='line', x=EduColumnName.TASK_NAME.value, y=MIN_COLUMN, color='blue', ax=ax)
    stats.plot(kind='line', x=EduColumnName.TASK_NAME.value, y=MAX_COLUMN, color='red', ax=ax)

    make_plot_pretty(ax, stats, plot_name('number of attempts', course_name), "number of attempts")

    return fig, ax


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        'preprocessed_course_data_path',
        type=str,
        help='Path to .csv file with preprocessed course data.',
    )
    parser.add_argument('course_structure_path', type=str, help='Path to .csv with the course structure.')
    parser.add_argument('--course-name', type=str, default=None, help='Name of the course.')


def main():
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args(sys.argv[1:])
    course_data = read_df(args.preprocessed_course_data_path)
    tasks_data_df = read_df(args.course_structure_path)

    stats = calculate_attempt_stats(course_data, tasks_data_df)
    plot_task_attempts(stats, args.course_name)
    plt.show()


if __name__ == '__main__':
    main()
