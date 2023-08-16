from typing import List, Optional

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from core.src.utils.df_utils import filter_df_by_single_value
from jba.src.models.edu_columns import EduTaskType, EduColumnName


def _get_tasks_colors(tasks_df: pd.DataFrame) -> List[str]:
    def _calculate_color(task_type: str):
        if task_type == EduTaskType.THEORY.value:
            return 'blue'
        if task_type == EduTaskType.UNDEFINED.value:
            return 'gray'
        return 'black'

    return list(map(lambda status: _calculate_color(status), tasks_df[EduColumnName.TASK_TYPE.value]))


def _calculate_task_type(course_data_df: pd.DataFrame, task_id: str) -> str:
    course_data_df = course_data_df[[EduColumnName.TASK_ID.value, EduColumnName.TASK_TYPE.value]]
    course_data_df = filter_df_by_single_value(course_data_df, EduColumnName.TASK_ID.value, task_id)
    task_type = course_data_df[EduColumnName.TASK_TYPE.value].unique()
    if len(task_type) == 1:
        return task_type[0]
    return EduTaskType.UNDEFINED.value


def _prepare_task_df_for_plots(course_data_df: pd.DataFrame, all_tasks_data_df: pd.DataFrame) -> pd.DataFrame:
    tasks_df = all_tasks_data_df[
        [EduColumnName.TASK_GLOBAL_NUMBER.value, EduColumnName.TASK_ID.value, EduColumnName.TASK_NAME.value]
    ].drop_duplicates().sort_values(EduColumnName.TASK_GLOBAL_NUMBER.value)
    tasks_df[EduColumnName.TASK_TYPE.value] = tasks_df.apply(
        lambda row: _calculate_task_type(course_data_df, row[EduColumnName.TASK_ID.value]), axis=1)
    return tasks_df


def _plot_name(base_name: str, course_name: Optional[str] = None) -> str:
    if course_name is not None:
        return f'{course_name} - {base_name}'
    return base_name


def _make_plot_pretty(ax, tasks_df: pd.DataFrame, course_name: Optional[str], ylabel: str):
    ax.set_xticks(np.arange(len(tasks_df[EduColumnName.TASK_NAME.value].values)))
    ax.set_xticklabels(tasks_df[EduColumnName.TASK_NAME.value])
    plt.xticks(rotation=90)
    plt.ylabel(ylabel)
    plt.xlabel("tasks")
    plt.title(course_name)
    [t.set_color(c) for t, c in zip(ax.xaxis.get_ticklabels(), _get_tasks_colors(tasks_df))]
    ax.margins(x=0)
    # plt.tick_params(axis='x', which='major', labelsize=7)
    plt.tight_layout()
