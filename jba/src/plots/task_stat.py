from dataclasses import dataclass
from typing import Dict

import pandas as pd

from core.src.model.column_name import SubmissionColumns
from core.src.utils.df_utils import filter_df_by_single_value
from jba.src.models.edu_columns import EduColumnName, EduTaskStatus


@dataclass(frozen=True)
class TaskStat:
    started: int
    finished: int
    finished_correct: int
    unfinished: int

    median_attempts: int
    min_attempts: int
    max_attempts: int


def calculate_tasks_stat(course_data_df: pd.DataFrame) -> Dict[int, TaskStat]:
    tasks = course_data_df[EduColumnName.TASK_ID.value].unique()
    stat = {}
    for task_id in tasks:
        task_data = filter_df_by_single_value(course_data_df, EduColumnName.TASK_ID.value, task_id)
        started_df = filter_df_by_single_value(task_data, SubmissionColumns.ATTEMPT.value, 1)
        started = started_df.shape[0]
        finished_df = task_data.loc[
            (task_data[SubmissionColumns.ATTEMPT.value] == task_data[SubmissionColumns.TOTAL_ATTEMPTS.value])]
        finished = finished_df.shape[0]
        finished_correct = filter_df_by_single_value(finished_df, EduColumnName.STATUS.value,
                                                     EduTaskStatus.CORRECT.value).shape[0]
        unfinished = filter_df_by_single_value(finished_df, EduColumnName.STATUS.value,
                                               EduTaskStatus.WRONG.value).shape[0]

        median_attempts = task_data[SubmissionColumns.ATTEMPT.value].median()
        min_attempts = task_data[SubmissionColumns.ATTEMPT.value].min()
        max_attempts = task_data[SubmissionColumns.ATTEMPT.value].max()

        stat[task_id] = TaskStat(started, finished, finished_correct, unfinished,
                                 median_attempts, min_attempts, max_attempts)
    return stat
