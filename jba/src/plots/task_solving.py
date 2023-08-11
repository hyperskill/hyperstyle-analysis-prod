import argparse
import sys
from typing import Dict, Optional

import matplotlib.pyplot as plt
import pandas as pd

from core.src.utils.df_utils import read_df
from jba.src.models.edu_columns import EduColumnName
from jba.src.plots.task_stat import TaskStat, _calculate_tasks_stat
from jba.src.plots.util import _prepare_task_df_for_plots, _plot_name, _make_plot_pretty


def _calculate_started_amount(tasks_stat: Dict[int, TaskStat], task_id: int) -> int:
    if task_id in tasks_stat:
        return tasks_stat[task_id].started
    return 0


def _calculate_finished_amount(tasks_stat: Dict[int, TaskStat], task_id: int) -> int:
    if task_id in tasks_stat:
        return tasks_stat[task_id].finished
    return 0


def _calculate_unfinished_correct_amount(tasks_stat: Dict[int, TaskStat], task_id: int) -> int:
    if task_id in tasks_stat:
        return tasks_stat[task_id].unfinished
    return 0


def plot_task_solving(course_data_df: pd.DataFrame, all_tasks_data_df: pd.DataFrame,
                      course_name: Optional[str] = None):
    started_column = 'started&finished'
    finished_correct_column = 'finished_correct'
    unfinished_column = 'unfinished'
    tasks_stat = _calculate_tasks_stat(course_data_df)

    tasks_df = _prepare_task_df_for_plots(course_data_df, all_tasks_data_df)
    tasks_df[started_column] = tasks_df.apply(
        lambda row: _calculate_started_amount(tasks_stat, row[EduColumnName.TASK_ID.value]), axis=1)
    tasks_df[finished_correct_column] = tasks_df.apply(
        lambda row: _calculate_finished_amount(tasks_stat, row[EduColumnName.TASK_ID.value]), axis=1)
    tasks_df[unfinished_column] = tasks_df.apply(
        lambda row: _calculate_unfinished_correct_amount(tasks_stat, row[EduColumnName.TASK_ID.value]), axis=1)

    plt.figure(dpi=300)
    ax = plt.gca()
    tasks_df.plot(kind='line', x=EduColumnName.TASK_NAME.value, y=started_column, color='red', ax=ax)
    tasks_df.plot(kind='line', x=EduColumnName.TASK_NAME.value, y=unfinished_column, color='black', ax=ax)
    _make_plot_pretty(ax, tasks_df, _plot_name('task solving process', course_name), "number of users")
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
    plot_task_solving(course_data, tasks_data_df, args.course_name)


if __name__ == '__main__':
    main()
