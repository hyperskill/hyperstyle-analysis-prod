import pandas as pd
import pytest

from core.model.column_name import IssuesColumns, SubmissionColumns
from core.utils.df_utils import read_df, equal_df
from templates.diffs.filter_by_diff import filter_template_issues_using_diff, create_templates_issues_df
from templates_tests.diffs import DIFF_TEMPLATE_ISSUES_FOLDER, SUBMISSIONS_FILE, STEPS_FILE

TEMPLATE_ISSUES_TEST_DATA = [
    (
        SUBMISSIONS_FILE,
        STEPS_FILE,
        SubmissionColumns.HYPERSTYLE_ISSUES.value,
        'filtered_submissions_python3_hyperstyle.csv',
        'template_issues.csv',
    ),
]


def prepare_template_issues_df(template_issues_df: pd.DataFrame) -> pd.DataFrame:
    template_issues_df = template_issues_df.reset_index(drop=True)
    template_issues_df[SubmissionColumns.STEP_ID.value] \
        = pd.to_numeric(template_issues_df[SubmissionColumns.STEP_ID.value])
    template_issues_df[IssuesColumns.POSITION.value] = pd.to_numeric(template_issues_df[IssuesColumns.POSITION.value])
    return template_issues_df


@pytest.mark.parametrize(
    ('submissions_path', 'steps_path', 'issues_column', 'result_path', 'template_issues'),
    TEMPLATE_ISSUES_TEST_DATA,
)
def test_filter_template_issues_using_diff(submissions_path: str,
                                           steps_path: str,
                                           issues_column: str,
                                           result_path: str,
                                           template_issues: str):
    df_submissions = read_df(DIFF_TEMPLATE_ISSUES_FOLDER / submissions_path)
    df_steps = read_df(DIFF_TEMPLATE_ISSUES_FOLDER / steps_path)
    df_filtered_issues = filter_template_issues_using_diff(df_submissions, df_steps, issues_column)

    df_result = read_df(DIFF_TEMPLATE_ISSUES_FOLDER / result_path)
    assert equal_df(df_result, df_filtered_issues)

    df_template_issues = create_templates_issues_df(df_filtered_issues, issues_column)
    df_template_issues_expected = read_df(DIFF_TEMPLATE_ISSUES_FOLDER / template_issues)
    assert equal_df(df_template_issues_expected, df_template_issues)
