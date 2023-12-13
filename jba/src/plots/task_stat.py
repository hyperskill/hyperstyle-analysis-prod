from dataclasses import dataclass
from typing import Dict

import pandas as pd

from core.src.model.column_name import SubmissionColumns
from jba.src.models.edu_columns import EduColumnName, EduTaskStatus


@dataclass(frozen=True)
class TaskStat:
    total_groups: int
    correct_groups: int
    wrong_groups: int

    median_attempts: int
    min_attempts: int
    max_attempts: int


def calculate_tasks_stat(course_data_df: pd.DataFrame) -> Dict[int, TaskStat]:
    stat = {}
    for task_id, task_data in course_data_df.groupby(EduColumnName.TASK_ID.value):  # noqa: WPS426
        total_groups = task_data[SubmissionColumns.GROUP.value].nunique()

        correct_groups = (
            task_data.groupby(SubmissionColumns.GROUP.value)
            .apply(lambda group: EduTaskStatus.CORRECT.value in group[EduColumnName.STATUS.value].unique())
            .sum()
        )

        wrong_groups = total_groups - correct_groups

        total_attempts_by_group = task_data.groupby(SubmissionColumns.GROUP.value).size()

        median_attempts = total_attempts_by_group.median()
        min_attempts = total_attempts_by_group.min()
        max_attempts = total_attempts_by_group.max()

        stat[task_id] = TaskStat(
            total_groups,
            correct_groups,
            wrong_groups,
            median_attempts,
            min_attempts,
            max_attempts,
        )

    return stat
