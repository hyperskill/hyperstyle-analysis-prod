import argparse
import sys
from typing import Dict, Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd

from core.src.utils.df_utils import read_df
from jba.src.models.edu_columns import EduColumnName
from jba.src.plots.task_stat import TaskStat, calculate_tasks_stat
from jba.src.plots.util import prepare_task_df_for_plots, plot_name, make_plot_pretty


def _calculate_total_user_amount(tasks_stat: Dict[int, TaskStat], task_id: int) -> int:
    stats = tasks_stat.get(task_id)
    if stats is None:
        return 0

    return stats.total_groups


def _calculate_users_that_solved_task(tasks_stat: Dict[int, TaskStat], task_id: int) -> int:
    stats = tasks_stat.get(task_id)
    if stats is None:
        return 0

    return stats.correct_groups


def _calculate_users_that_failed_task(tasks_stat: Dict[int, TaskStat], task_id: int) -> int:
    stats = tasks_stat.get(task_id)
    if stats is None:
        return 0

    return stats.wrong_groups


TOTAL_COLUMN = 'total'
SOLVED_COLUMN = 'solved'
FAILED_COLUMN = 'failed'


def calculate_solving_stats(course_data_df: pd.DataFrame, all_tasks_data_df: pd.DataFrame) -> pd.DataFrame:
    tasks_stat = calculate_tasks_stat(course_data_df)
    tasks_df = prepare_task_df_for_plots(course_data_df, all_tasks_data_df)

    tasks_df[TOTAL_COLUMN] = tasks_df.apply(
        lambda row: _calculate_total_user_amount(tasks_stat, row[EduColumnName.TASK_ID.value]),
        axis=1,
    )
    tasks_df[SOLVED_COLUMN] = tasks_df.apply(
        lambda row: _calculate_users_that_solved_task(tasks_stat, row[EduColumnName.TASK_ID.value]),
        axis=1,
    )
    tasks_df[FAILED_COLUMN] = tasks_df.apply(
        lambda row: _calculate_users_that_failed_task(tasks_stat, row[EduColumnName.TASK_ID.value]),
        axis=1,
    )

    return tasks_df


def plot_task_solving(stats: pd.DataFrame, course_name: Optional[str] = None) -> Tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(dpi=300)

    stats.plot(kind='line', x=EduColumnName.TASK_NAME.value, y=TOTAL_COLUMN, color='black', ax=ax)
    stats.plot(kind='line', x=EduColumnName.TASK_NAME.value, y=SOLVED_COLUMN, color='green', ax=ax)
    stats.plot(kind='line', x=EduColumnName.TASK_NAME.value, y=FAILED_COLUMN, color='red', ax=ax)

    make_plot_pretty(ax, stats, plot_name('task solving process', course_name), "number of users")

    return fig, ax


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        'preprocessed_course_data_path', type=str, help='Path to .csv file with preprocessed course data.'
    )
    parser.add_argument('course_structure_path', type=str, help='Path to .csv with the course structure.')
    parser.add_argument('--course-name', type=str, default=None, help='Name of the course.')


def main():
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args(sys.argv[1:])
    course_data = read_df(args.preprocessed_course_data_path)
    tasks_data_df = read_df(args.course_structure_path)

    stats = calculate_solving_stats(course_data, tasks_data_df)
    plot_task_solving(stats, args.course_name)
    plt.show()


if __name__ == '__main__':
    main()
