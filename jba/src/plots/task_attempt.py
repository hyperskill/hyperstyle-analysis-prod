import argparse
import sys
from typing import Optional, Dict

import matplotlib.pyplot as plt
import pandas as pd

from core.src.utils.df_utils import read_df
from jba.src.models.edu_columns import EduColumnName
from jba.src.plots.task_stat import TaskStat, _calculate_tasks_stat
from jba.src.plots.util import _prepare_task_df_for_plots, _make_plot_pretty, _plot_name


def _calculate_median(tasks_stat: Dict[int, TaskStat], task_id: int) -> int:
    if task_id in tasks_stat:
        return tasks_stat[task_id].median_attempts
    return 0


def _calculate_min(tasks_stat: Dict[int, TaskStat], task_id: int) -> int:
    if task_id in tasks_stat:
        return tasks_stat[task_id].min_attempts
    return 0


def _calculate_max(tasks_stat: Dict[int, TaskStat], task_id: int) -> int:
    if task_id in tasks_stat:
        return tasks_stat[task_id].max_attempts
    return 0


def plot_task_attempts(course_data_df: pd.DataFrame, all_tasks_data_df: pd.DataFrame,
                       course_name: Optional[str] = None):
    tasks_stat = _calculate_tasks_stat(course_data_df)

    median_attempts_count_column = 'median'
    min_attempts_count_column = 'min'
    max_attempts_count_column = 'max'

    tasks_df = _prepare_task_df_for_plots(course_data_df, all_tasks_data_df)
    tasks_df[median_attempts_count_column] = tasks_df.apply(
        lambda row: _calculate_median(tasks_stat, row[EduColumnName.TASK_ID.value]), axis=1)
    tasks_df[min_attempts_count_column] = tasks_df.apply(
        lambda row: _calculate_min(tasks_stat, row[EduColumnName.TASK_ID.value]), axis=1)
    tasks_df[max_attempts_count_column] = tasks_df.apply(
        lambda row: _calculate_max(tasks_stat, row[EduColumnName.TASK_ID.value]), axis=1)

    plt.figure(dpi=300)
    ax = plt.gca()
    tasks_df.plot(kind='line', x=EduColumnName.TASK_NAME.value, y=median_attempts_count_column, color='black', ax=ax)
    tasks_df.plot(kind='line', x=EduColumnName.TASK_NAME.value, y=min_attempts_count_column, color='blue', ax=ax)
    tasks_df.plot(kind='line', x=EduColumnName.TASK_NAME.value, y=max_attempts_count_column, color='red', ax=ax)
    _make_plot_pretty(ax, tasks_df, _plot_name('number of attempts', course_name), "number of attempts")
    plt.show()


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('preprocessed_course_data_path', type=str, help='Path to .csv file with preprocessed course data.')
    parser.add_argument('course_structure_path', type=str, help='Path to .csv with the course structure.')
    parser.add_argument('--course-name', type=str, default=None, help='Name of the course.')


def main():
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args(sys.argv[1:])
    course_data = read_df(args.preprocessed_course_data_path)
    tasks_data_df = read_df(args.course_structure_path)
    plot_task_attempts(course_data, tasks_data_df, args.course_name)


if __name__ == '__main__':
    main()
