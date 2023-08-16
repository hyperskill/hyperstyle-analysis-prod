from typing import List

import pandas as pd
import pytest

from jba.src.models.edu_columns import EduColumnName
from jba.src.plots.task_duplicates import _count_duplicates_submissions

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
    assert _count_duplicates_submissions(group) == expected_duplicates
