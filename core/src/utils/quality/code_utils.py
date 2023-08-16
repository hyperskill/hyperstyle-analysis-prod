from typing import List, Optional

import pandas as pd

from core.src.model.column_name import SubmissionColumns
from core.src.utils.quality.report_utils import get_language_version, parse_report


def split_code_to_lines(code: str, keep_ends: bool = False) -> List[str]:
    """ Split code to lines. Considers both line separations models (with and without \r). """

    return code.splitlines(keep_ends)


def get_code_with_issue_comment(submission: pd.Series, issues_column: str,
                                issue_name: Optional[str] = None,
                                issue_line_number: Optional[int] = None) -> str:
    """ Add comment to code lines where issues appear in submission. """

    code_lines = split_code_to_lines(submission[SubmissionColumns.CODE.value])
    language_version = get_language_version(submission[SubmissionColumns.LANG.value])

    report = parse_report(submission, issues_column)
    for issue in report.get_issues():
        if issue_name is None or issue.get_name() == issue_name:
            if issue_line_number is None or issue.get_line_number() == issue_line_number:
                code_lines[issue.get_line_number() - 1] += get_comment_to_code_line(issue, language_version)

    return merge_lines_to_code(code_lines)

