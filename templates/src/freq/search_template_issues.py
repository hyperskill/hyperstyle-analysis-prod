import argparse
from pathlib import Path

import sys
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import pandas as pd

from core.src.model.column_name import SubmissionColumns, IssuesColumns, StepColumns
from core.src.model.quality.issue.issue import BaseIssue
from core.src.utils.df_utils import filter_df_by_iterable_value, read_df, write_or_pint_df
from core.src.utils.logging_utils import configure_logger
from core.src.utils.quality.code_utils import split_code_to_lines
from core.src.utils.quality.report_utils import parse_report
from templates.src.freq.matching.template_matching import match_code_with_template
from templates.src.freq.utils.code_comparator import CodeComparator
from templates.src.freq.utils.template_columns import TemplateColumns
from templates.src.utils.template_utils import parse_template_code_from_step


@dataclass(frozen=True)
class RepetitiveIssue:
    name: str
    template_line_number: Optional[int]
    line_with_issue: Optional[str]

    # Other field are do not included to __eq__ method
    base_issue: Optional[BaseIssue] = field(compare=False, hash=False)
    submission: Optional[pd.Series] = field(compare=False, hash=False)


def get_repetitive_issues(submission_series: pd.DataFrame,
                          template_lines: List[str],
                          issues_column: str,
                          code_comparator: CodeComparator) -> List[RepetitiveIssue]:
    """
    Get information about issue (name, position in template, etc.) for issues
    that appear in every attempt in submission series.
    """

    repetitive_issues_dict = defaultdict(list)
    submission_series = submission_series.sort_values(SubmissionColumns.ATTEMPT.value)

    for _, submission in submission_series.iterrows():
        code_lines = split_code_to_lines(submission[SubmissionColumns.CODE.value])
        code_to_template, _ = match_code_with_template(code_lines, template_lines,
                                                       code_comparator.is_equal,
                                                       code_comparator.is_empty)

        report = parse_report(submission, issues_column)
        for issue in report.get_issues():
            issue_name = issue.get_name()
            # In issues line count starts with 1
            code_line_number = issue.get_line_number() - 1
            line_with_issue = None
            pos_in_template = None

            # Some issues have zero line number meaning they do not have exact position and line
            if code_line_number >= 0:
                pos_in_template = code_to_template[code_line_number]
                if pos_in_template is not None:
                    line_with_issue = template_lines[pos_in_template]
                else:
                    line_with_issue = code_lines[code_line_number]
                line_with_issue = code_comparator.preprocess(line_with_issue)
            repetitive_issue = RepetitiveIssue(issue_name, pos_in_template, line_with_issue, issue, submission)
            repetitive_issues_dict[repetitive_issue].append(repetitive_issue)

    total_attempts_count = submission_series.shape[0]

    # Repetitive issues are which appear in all attempts
    return [
        key_issue
        for key_issue, repetitive_issues in repetitive_issues_dict.items()
        if len(repetitive_issues) == total_attempts_count
    ]


def repetitive_issues_to_df(step_id: int,
                            step_submissions_count: int,
                            repetitive_issues: Dict[RepetitiveIssue, List[RepetitiveIssue]]) -> pd.DataFrame:
    """ Convert all collected repetitive issues information from dict to dataframe. """
    repetitive_issues_series = []

    for key_issue, repetitive_issues in repetitive_issues.items():
        repetitive_issue = {IssuesColumns.NAME.value: key_issue.name,
                            TemplateColumns.DESCRIPTION.value: key_issue.base_issue.get_text(),
                            TemplateColumns.LINE.value: key_issue.line_with_issue,
                            TemplateColumns.POS_IN_TEMPLATE.value: key_issue.template_line_number,
                            TemplateColumns.COUNT.value: len(repetitive_issues),
                            TemplateColumns.GROUPS.value:
                                [issue.submission[SubmissionColumns.GROUP.value] for issue in repetitive_issues]}
        repetitive_issues_series.append(pd.Series(repetitive_issue))

    df_repetitive_issues = pd.DataFrame.from_records(repetitive_issues_series)

    df_repetitive_issues[TemplateColumns.POS_IN_TEMPLATE.value] = \
        df_repetitive_issues[TemplateColumns.POS_IN_TEMPLATE.value].astype('Int64')

    df_repetitive_issues[TemplateColumns.TOTAL_COUNT.value] = step_submissions_count
    df_repetitive_issues[SubmissionColumns.STEP_ID.value] = step_id

    df_repetitive_issues[TemplateColumns.FREQUENCY.value] = \
        df_repetitive_issues[TemplateColumns.COUNT.value] / df_repetitive_issues[TemplateColumns.TOTAL_COUNT.value]

    return df_repetitive_issues.sort_values(by=TemplateColumns.COUNT.value, ascending=False)


def search_repetitive_issues_by_step(df_submissions: pd.DataFrame,
                                     step: pd.Series,
                                     issues_column: str,
                                     code_comparator: CodeComparator) -> pd.DataFrame:
    """ Search template issues in submissions with given step. """

    step_ids = df_submissions[SubmissionColumns.STEP_ID.value].unique()
    assert len(step_ids) == 1, "All submissions should be for single step"

    langs = df_submissions[SubmissionColumns.LANG.value].unique()
    assert len(langs) == 1, "Can not process search for submissions with different language version"

    template = parse_template_code_from_step(step, langs[0])
    repetitive_issues = defaultdict(list)

    df_submission_series = df_submissions.groupby(SubmissionColumns.GROUP.value)
    for _, submission_series in df_submission_series:
        submission_series_repetitive_issues = get_repetitive_issues(submission_series, template, issues_column,
                                                                    code_comparator)
        for issue in submission_series_repetitive_issues:
            repetitive_issues[issue].append(issue)

    return repetitive_issues_to_df(step[StepColumns.ID.value], df_submissions.shape[0], repetitive_issues)


def search_repetitive_issues(df_submissions: pd.DataFrame,
                             df_steps: pd.DataFrame,
                             issues_column: str,
                             code_comparator: CodeComparator) -> pd.DataFrame:
    """ Search for all repetitive issues - issue which remains in all submission of concrete user for concrete step. """

    df_submissions = filter_df_by_iterable_value(df_submissions, SubmissionColumns.STEP_ID.value,
                                                 df_steps[StepColumns.ID.value].unique())

    df_steps.set_index(StepColumns.ID.value, inplace=True, drop=False)

    return df_submissions \
        .groupby([SubmissionColumns.STEP_ID.value], as_index=False) \
        .apply(lambda df_step_submissions: search_repetitive_issues_by_step(df_step_submissions,
                                                                            # name is group key (step id)
                                                                            step=df_steps.loc[df_step_submissions.name],
                                                                            issues_column=issues_column,
                                                                            code_comparator=code_comparator))


def search_template_issues(submissions_path: str, steps_path: str, repetitive_issues_path: Optional[str],
                           issues_column: str, equal_type: str, ignore_trailing_comments: bool,
                           ignore_trailing_whitespaces: bool):
    """ Search for all repetitive issues and save result to `repetitive_issues_path` """

    df_submissions = read_df(submissions_path)
    df_steps = read_df(steps_path)

    code_comparator = CodeComparator(equal_type, ignore_trailing_comments, ignore_trailing_whitespaces)
    df_repetitive_issues = search_repetitive_issues(df_submissions, df_steps, issues_column, code_comparator)
    write_or_pint_df(df_repetitive_issues, repetitive_issues_path)


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('submissions_path', type=str, help='Path to .csv file with submissions.')
    parser.add_argument('steps_path', type=str, help='Path to .csv file with steps.')
    parser.add_argument('issues_column', type=str,
                        help='Column where issues stored.',
                        choices=[SubmissionColumns.HYPERSTYLE_ISSUES.value, SubmissionColumns.QODANA_ISSUES.value])

    parser.add_argument(
        '--output-path', type=str, default=None,
        help='Path .csv file with repetitive issues search result. '
             'If no value was passed, the output will be printed into the console.'
    )
    parser.add_argument('--equal', type=str, default='edit_distance',
                        help='Function for lines comparing.',
                        choices=['edit_distance', 'edit_ratio', 'substring'])
    parser.add_argument('-ic', '--ignore-trailing-comments', action='store_true',
                        help='Ignore trailing comments in code compare. True by default.')
    parser.add_argument('-iw', '--ignore-trailing-whitespaces', action='store_true',
                        help='Ignore trailing whitespaces in code compare. True by default.')

    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')


def main():
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args(sys.argv[1:])
    if args.output_path is None:
        log_file_suffix = Path(args.submissions_path).parent
    else:
        log_file_suffix = args.output_path
    configure_logger(log_file_suffix, f'repetitive_issues_{args.equal}', args.log_path)

    search_template_issues(args.submissions_path, args.steps_path, args.output_path, args.issues_column,
                           args.equal, args.ignore_trailing_comments, args.ignore_trailing_whitespaces)


if __name__ == '__main__':
    main()
