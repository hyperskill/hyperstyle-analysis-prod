from typing import List, Optional

import pandas as pd
import pytest
from pandas._testing import assert_series_equal

from core.src.model.column_name import SubmissionColumns
from jba.src.models.edu_columns import EduColumnName
from jba.src.plots.task_duplicates import (
    _count_duplicates_submissions,
    _compute_stats,
    MIN_STATS_COLUMN,
    MAX_STATS_COLUMN,
    MEDIAN_STATS_COLUMN,
    MEAN_STATS_COLUMNS,
)

COUNT_DUPLICATES_TEST_DATA = [
    (pd.DataFrame(), []),
    (pd.DataFrame({EduColumnName.CODE_SNIPPETS.value: ['A']}), []),
    (pd.DataFrame({EduColumnName.CODE_SNIPPETS.value: ['A', 'A']}), [1]),
    (pd.DataFrame({EduColumnName.CODE_SNIPPETS.value: ['A', 'B', 'C']}), []),
    (pd.DataFrame({EduColumnName.CODE_SNIPPETS.value: ['A', 'B', 'A']}), []),
    (pd.DataFrame({EduColumnName.CODE_SNIPPETS.value: ['A', 'A', 'B']}), [1]),
    (pd.DataFrame({EduColumnName.CODE_SNIPPETS.value: ['A', 'A', 'A']}), [2]),
    (pd.DataFrame({EduColumnName.CODE_SNIPPETS.value: ['A', 'A', 'B', 'C', 'C', 'C', 'D', 'C']}), [1, 2]),
]


@pytest.mark.parametrize(('group', 'expected_duplicates'), COUNT_DUPLICATES_TEST_DATA)
def test_count_duplicates(group: pd.DataFrame, expected_duplicates: List[int]):
    group.name = 0
    assert _count_duplicates_submissions(group) == expected_duplicates


COURSE_DATA = pd.DataFrame(
    [
        [1, 6, 'A'],
        [1, 6, 'B'],
        [2, 1, 'A'],
        [2, 2, 'A'],
        [2, 2, 'B'],
        [2, 2, 'C'],
        [3, 3, 'A'],
        [3, 3, 'B'],
        [3, 3, 'B'],
        [3, 3, 'B'],
        [3, 3, 'A'],
        [3, 3, 'C'],
        [3, 4, 'A'],
        [3, 4, 'B'],
        [3, 4, 'A'],
        [3, 5, 'A'],
        [3, 5, 'A'],
        [3, 5, 'A'],
        [3, 5, 'A'],
        [3, 5, 'A'],
        [3, 5, 'B'],
        [4, 7, 'A'],
        [4, 7, 'A'],
        [4, 7, 'B'],
        [4, 8, 'A'],
        [4, 8, 'A'],
        [4, 8, 'A'],
        [4, 8, 'A'],
        [4, 8, 'B'],
        [4, 8, 'A'],
        [4, 8, 'A'],
        [4, 9, 'A'],
        [4, 9, 'A'],
        [4, 9, 'B'],
        [4, 9, 'B'],
        [4, 9, 'C'],
        [4, 9, 'C'],
        [4, 9, 'D'],
        [4, 9, 'D'],
        [4, 9, 'E'],
        [4, 9, 'E'],
    ],
    columns=[EduColumnName.TASK_ID.value, SubmissionColumns.GROUP.value, EduColumnName.CODE_SNIPPETS.value],
)


COMPUTE_STATA_TEST_DATA = [
    (0, None),
    (1, pd.Series({MIN_STATS_COLUMN: 0.0, MAX_STATS_COLUMN: 0.0, MEAN_STATS_COLUMNS: 0.0, MEDIAN_STATS_COLUMN: 0.0})),
    (2, pd.Series({MIN_STATS_COLUMN: 0.0, MAX_STATS_COLUMN: 0.0, MEAN_STATS_COLUMNS: 0.0, MEDIAN_STATS_COLUMN: 0.0})),
    (3, pd.Series({MIN_STATS_COLUMN: 0.0, MAX_STATS_COLUMN: 4.0, MEAN_STATS_COLUMNS: 2.0, MEDIAN_STATS_COLUMN: 2.0})),
    (4, pd.Series({MIN_STATS_COLUMN: 1.0, MAX_STATS_COLUMN: 3.0, MEAN_STATS_COLUMNS: 5/3, MEDIAN_STATS_COLUMN: 1.0})),
]


@pytest.mark.parametrize(('task_id', 'expected_stats'), COMPUTE_STATA_TEST_DATA)
def test_compute_stats(task_id: int, expected_stats: Optional[pd.Series]):
    actual_stats = _compute_stats(task_id, COURSE_DATA)
    if expected_stats is None:
        assert actual_stats is None
    else:
        assert_series_equal(actual_stats, expected_stats)
