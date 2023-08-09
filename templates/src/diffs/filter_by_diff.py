import argparse
import ast
import bisect
from pathlib import Path
from typing import List, Tuple, Optional

import pandas as pd
import sys
from diff_match_patch import diff_match_patch

from core.src.model.column_name import SubmissionColumns, StepColumns, IssuesColumns
from core.src.model.quality.issue.issue import BaseIssue
from core.src.utils.df_utils import filter_df_by_iterable_value, read_df, write_df, write_or_pint_df
from core.src.utils.logging_utils import configure_logger
from core.src.utils.quality.code_utils import split_code_to_lines
from core.src.utils.quality.report_utils import parse_report, parse_str_report
from templates.src.diffs.model.diff_interval import DiffInterval
from templates.src.diffs.model.diff_result import DiffResult
from templates.src.diffs.model.diff_tag import DiffTag
from templates.src.utils.template_utils import parse_template_code_from_step, is_comment

DIF_SUFFIX = 'diff'
DIFF_TEMPLATE_POSITIONS_SUFFIX = 'diff_template_positions'


def get_code_prefix_lengths(code_lines: List[str]) -> List[int]:
    code_prefix_length = [0]
    for code_line in code_lines:
        code_prefix_length.append(code_prefix_length[-1] + len(code_line))

    return code_prefix_length


def issues_positions_to_offsets(issues: List[BaseIssue], code_lines: List[str]) -> List[int]:
    """ For each issue calculate offset in code written in one line and return as pairs sorted in ascending order."""

    code_prefix_lengths = get_code_prefix_lengths(code_lines)

    issues_offsets = []
    for issue in issues:
        if issue.get_line_number() == 0:
            issues_offsets.append(0)
        issue_offset = code_prefix_lengths[issue.get_line_number() - 1] + issue.get_column_number()
        issues_offsets.append(issue_offset)

    return issues_offsets


def issues_offsets_to_positions(offsets: List[int], code_lines: List[str]) -> List[Tuple[int, int]]:
    code_prefix_lengths = get_code_prefix_lengths(code_lines)

    issues_positions = []
    for offset in offsets:
        line_number = bisect.bisect_right(code_prefix_lengths, offset)
        if line_number == 0:
            column_number = offset
        else:
            column_number = offset - code_prefix_lengths[line_number - 1]
        issues_positions.append((line_number, column_number))

    return issues_positions


def to_cleanup_semantic(template_lines: List[str], code_lines: List[str]) -> bool:
    """
    Indicates if we should to apply the <diff_cleanupEfficiency> function
    See: https://github.com/google/diff-match-patch/wiki/API#diff_cleanupsemanticdiffs--null

    If the template contains a comment, and the user deleted this comment (or vice versa),
    and the comment partially contains constructs from the code, e.g. names or variables or keywords,
    then the diffs are built inconsistently, and we should combine additions and deletions into a readable format.

    Consider an example:

    1) The template code:

    def foo():

        # You already are within the body of func foo()
        # Declare and assign the correct value to the 'varchest' variable below:

        print(varchest)

    2) The user code:

    def foo():

        varchest = "gold"

        print(varchest)

    In this case we will get the following set of diffs:
    [
        (0, 'def foo():\n\n    '),
        (-1, "# You already are within the body of func foo()\n    # Declare and assign the correct value to the '"),
        (0, 'varchest'),
        (-1, "'"), (0, ' '), (-1, 'variable'),
        (1, '='), (0, ' '), (-1, 'bel'), (1, '"g'), (0, 'o'), (-1, 'w:'), (1, 'ld"'),
        (0, '\n\n    print(varchest)')
    ]

    The comment and the variable definition are mixed,
    so if we use <diff_cleanupEfficiency> the additional and deletions will be merged:
    [
        (0, 'def foo():\n\n    '),
        (-1, "# You already are within the body of func foo()\n    # Declare and assign the correct value to the 'varchest' variable below:"),
        (1, 'varchest = "gold"'),
        (0, '\n\n    print(varchest)')
    ]

    See more examples in tests.
    """
    template_comments = filter(is_comment, template_lines)
    code_comments = filter(is_comment, code_lines)
    return any(x not in template_comments for x in code_comments) or any(
        x not in code_comments for x in template_comments)


def get_template_to_code_diffs(template_lines: List[str], code_lines: List[str]) -> List[DiffResult]:
    """ Get template to students code diffs. """

    matcher = diff_match_patch()
    patches = matcher.diff_main(''.join(template_lines), ''.join(code_lines))
    if to_cleanup_semantic(template_lines, code_lines):
        matcher.diff_cleanupSemantic(patches)

    diffs = []
    code_start, code_end = 0, 0
    template_start, template_end = 0, 0

    for tag, patch in patches:
        if tag == DiffTag.ADDITION.value:
            code_end = code_start + len(patch)

        if tag == DiffTag.EQUAL.value:
            code_end = code_start + len(patch)
            template_end = template_start + len(patch)

        if tag == DiffTag.DELETION.value:
            template_end = template_start + len(patch)

        diffs.append(
            DiffResult(tag, patch, DiffInterval(template_start, template_end), DiffInterval(code_start, code_end)))
        code_start = code_end
        template_start = template_end

    return diffs


def get_template_issues(issues: List[BaseIssue], issues_offsets: List[int], diffs: List[DiffResult]) \
        -> Tuple[List[BaseIssue], List[int]]:
    """
    Get template issues from list of issues.
    Issues considered as template if it's position inside change in diff with type 0 - code not changed from template.
    """

    i = 0
    template_issues = []
    template_issues_offsets = []

    for issue, offset in sorted(zip(issues, issues_offsets), key=lambda p: p[1]):
        while i < len(diffs):
            diff = diffs[i]

            # If code interval is before issue offset continue
            if diff.code_interval.end < offset or diff.tag != DiffTag.EQUAL.value:
                i += 1
                continue

            # If issue is inside code interval and tag is "equal" consider issue as template
            interval_offset = offset - diff.code_interval.start
            template_offset = diff.template_interval.start + interval_offset
            template_issues.append(issue)
            template_issues_offsets.append(template_offset)
            break

    return template_issues, template_issues_offsets


def filter_in_single_submission(submission: pd.Series, step: pd.Series, issues_column: str) -> pd.Series:
    code_lines = split_code_to_lines(submission[SubmissionColumns.CODE.value], keep_ends=True)
    lang = submission[SubmissionColumns.LANG.value]
    template_lines = parse_template_code_from_step(step, lang, keep_ends=True)

    report = parse_report(submission, issues_column)
    issues = report.get_issues()
    issues_offsets = issues_positions_to_offsets(issues, code_lines)
    diff = get_template_to_code_diffs(template_lines, code_lines)
    template_issues, template_issues_offsets = get_template_issues(issues, issues_offsets, diff)
    template_issues_positions = issues_offsets_to_positions(template_issues_offsets, template_lines)

    submission[issues_column] = report.filter_issues(lambda i: i not in template_issues).to_json()
    submission[f'{issues_column}_{DIF_SUFFIX}'] = report.filter_issues(lambda i: i in template_issues).to_json()
    submission[f'{issues_column}_all'] = report.to_json()
    submission[f'{issues_column}_{DIFF_TEMPLATE_POSITIONS_SUFFIX}'] = str(template_issues_positions)

    return submission


def filter_template_issues_using_diff(df_submissions: pd.DataFrame, df_steps: pd.DataFrame, issues_column: str) \
        -> pd.DataFrame:
    df_submissions = filter_df_by_iterable_value(df_submissions, SubmissionColumns.STEP_ID.value,
                                                 df_steps[StepColumns.ID.value].unique())
    df_steps.set_index(StepColumns.ID.value, inplace=True, drop=False)

    def apply_filter(submission):
        return filter_in_single_submission(submission,
                                           issues_column=issues_column,
                                           step=df_steps.loc[submission[SubmissionColumns.STEP_ID.value]])

    return df_submissions.apply(lambda submission: apply_filter(submission), axis=1)


def main(
        submissions_path: str,
        steps_path: str,
        filtered_submissions_path: Optional[str],
        issues_column: str,
        templates_issues_path: Optional[str],
):
    df_submissions = read_df(submissions_path)
    df_steps = read_df(steps_path)
    df_filtered_issues = filter_template_issues_using_diff(
        df_submissions,
        df_steps,
        issues_column,
    )
    write_or_pint_df(df_filtered_issues, filtered_submissions_path)

    if templates_issues_path is not None:
        template_issues_df = create_templates_issues_df(df_filtered_issues, issues_column)
        write_df(template_issues_df, templates_issues_path)


def create_templates_issues_df(df_filtered_issues: pd.DataFrame, issues_column: str) -> pd.DataFrame:
    row_number_column = 'row_number'
    offset_column = 'offset'
    issues_dict = {
        SubmissionColumns.STEP_ID.value: [],
        IssuesColumns.NAME.value: [],
        IssuesColumns.CATEGORY.value: [],
        IssuesColumns.DIFFICULTY.value: [],
        IssuesColumns.TEXT.value: [],
        row_number_column: [],
        offset_column: [],
    }

    def unzip_issue(row: pd.Series):
        report = parse_str_report(row[f'{issues_column}_{DIF_SUFFIX}'], issues_column)
        issues = report.get_issues()
        positions = ast.literal_eval(row[f'{issues_column}_{DIFF_TEMPLATE_POSITIONS_SUFFIX}'])
        step_id = row[SubmissionColumns.STEP_ID.value]
        for issue, pos in zip(issues, positions):
            issues_dict[SubmissionColumns.STEP_ID.value].append(step_id)
            issues_dict[IssuesColumns.NAME.value].append(issue.get_name())
            issues_dict[IssuesColumns.CATEGORY.value].append(issue.get_category())
            issues_dict[IssuesColumns.DIFFICULTY.value].append(issue.get_difficulty())
            issues_dict[IssuesColumns.TEXT.value].append(issue.get_text())
            row_number, offset = pos
            issues_dict[row_number_column].append(row_number)
            issues_dict[offset_column].append(offset)

    df_filtered_issues.apply(lambda row: unzip_issue(row), axis=1)
    return pd.DataFrame.from_dict(issues_dict).drop_duplicates(subset=[
        SubmissionColumns.STEP_ID.value,
        IssuesColumns.NAME.value,
        IssuesColumns.CATEGORY.value,
        IssuesColumns.DIFFICULTY.value,
        row_number_column,
        offset_column,
    ])


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('submissions_path', type=str, help='Path to .csv file with submissions.')
    parser.add_argument('steps_path', type=str, help='Path to .csv file with steps.')
    parser.add_argument('issues_column', type=str,
                        help='Column where issues stored.',
                        choices=[SubmissionColumns.HYPERSTYLE_ISSUES.value, SubmissionColumns.QODANA_ISSUES.value])

    parser.add_argument(
        '--output-path', type=str, default=None,
        help='Path .csv file with submissions with filtered template issues. '
             'If no value was passed, the output will be printed into the console.'
    )
    parser.add_argument(
        '--templates-issues-path', type=str, default=None,
        help='Path .csv file with template issues in the user-friendly format. '
             'By default it is None and does not create this file.'
    )
    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args(sys.argv[1:])
    if args.output_path is None:
        log_file_suffix = Path(args.submissions_path).parent
    else:
        log_file_suffix = args.output_path
    configure_logger(log_file_suffix, 'template_issues_filtering_by_diff', args.log_path)

    main(
        args.submissions_path,
        args.steps_path,
        args.output_path,
        args.issues_column,
        args.templates_issues_path,
    )
