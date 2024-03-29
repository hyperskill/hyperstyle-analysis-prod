from typing import List, Optional, Tuple, Union

import pytest

from core.src.model.column_name import SubmissionColumns
from core.src.utils.df_utils import read_df
from templates.src.freq.search_template_issues import RepetitiveIssue, get_repetitive_issues
from templates.src.freq.utils.code_comparator import CodeComparator
from templates.tests.freq import FREQ_TEMPLATE_ISSUES_FOLDER

REPETITIVE_ISSUES_FOLDER = FREQ_TEMPLATE_ISSUES_FOLDER / 'repetitive_issues'
LINES_TEST_DATA = [
    ('in_1_submission_series_python3_hyperstyle.csv',
     ['e = 2.718281828459045',
      '# put your python code here'],
     SubmissionColumns.HYPERSTYLE_ISSUES.value,
     'edit_distance', False, False, 0, [RepetitiveIssue('WPS446', 0, 'e = 2.718281828459045', None, None)]),
    ('in_2_submission_series_python3_hyperstyle.csv',
     ['e = 2.718281828459045',
      '# put your python code here'],
     SubmissionColumns.HYPERSTYLE_ISSUES.value,
     'edit_distance', False, False, 0, [RepetitiveIssue('WPS446', 0, 'e = 2.718281828459045', None, None),
                                        RepetitiveIssue('WPS237', None, 'print(f"{e:.5f}")', None, None)]),
    ('in_3_submission_series_python3_hyperstyle.csv',
     ['e = 2.718281828459045',
      '# put your python code here'],
     SubmissionColumns.HYPERSTYLE_ISSUES.value,
     'edit_distance', False, False, 0, []),
]


@pytest.mark.parametrize(
    ('submission_series_path', 'template_lines', 'issues_column', 'equal_type',
     'ignore_trailing_comments', 'ignore_trailing_whitespaces', 'equal_upper_bound', 'repetitive_issues'),
    LINES_TEST_DATA,
)
def test_get_repetitive_issues(submission_series_path: str,
                               template_lines: List[str],
                               issues_column: str,
                               equal_type: str,
                               ignore_trailing_comments: bool,
                               ignore_trailing_whitespaces: bool,
                               equal_upper_bound: Optional[Union[int, float]],
                               repetitive_issues: List[Tuple[str, int]]):
    df_submission_series = read_df(REPETITIVE_ISSUES_FOLDER / submission_series_path)

    code_comparator = CodeComparator(equal_type, ignore_trailing_comments,
                                     ignore_trailing_whitespaces, equal_upper_bound)

    actual_repetitive_issues = \
        get_repetitive_issues(df_submission_series, template_lines, issues_column, code_comparator)

    assert set(actual_repetitive_issues) == set(repetitive_issues)
