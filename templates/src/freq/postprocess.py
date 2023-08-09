import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd

from core.src.model.api.platform_objects import Object
from core.src.model.column_name import SubmissionColumns, IssuesColumns, StepColumns
from core.src.utils.df_utils import read_df, write_df
from core.src.utils.file.extension_utils import AnalysisExtension
from core.src.utils.file.file_utils import create_directory
from core.src.utils.file.saving_utils import save_solution_to_file
from core.src.utils.logging_utils import configure_logger
from core.src.utils.quality.code_utils import get_code_with_issue_comment
from templates.src.freq.utils.template_columns import TemplateColumns


@dataclass(frozen=True)
class ProcessingConfig(Object):
    repetitive_issues_path: str
    result_path: Optional[str]
    submissions_path: Optional[str]
    issues_column: Optional[str]
    freq_to_remove: float
    freq_to_separate_template_issues: float
    freq_to_separate_rare_and_common_issues: float
    solutions_number: int
    with_additional_info: bool
    base_task_url: str

    @staticmethod
    def parse_from_args(args) -> 'ProcessingConfig':
        return ProcessingConfig(
            repetitive_issues_path=args.repetitive_issues_path,
            submissions_path=args.submissions_path,
            result_path=args.output_path,
            issues_column=args.issues_column,
            freq_to_remove=args.freq_to_remove / 100,
            freq_to_separate_template_issues=args.freq_to_separate_template_issues / 100,
            freq_to_separate_rare_and_common_issues=args.freq_to_separate_rare_and_common_issues / 100,
            solutions_number=args.solutions_number,
            with_additional_info=args.with_additional_info,
            base_task_url=args.base_task_url.rstrip('/'),
        )


def get_partition_by_pos_in_template(df_repetitive_issues: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split issues into to two group according to `pos_in_template` value:
    first group is with None position in template (not specified) and second with detected position.
    """

    df_with_pos_in_template = df_repetitive_issues[
        df_repetitive_issues[SubmissionColumns.POS_IN_TEMPLATE.value].notnull()]

    df_without_pos_in_template = df_repetitive_issues[
        df_repetitive_issues[SubmissionColumns.POS_IN_TEMPLATE.value].isnull()]

    return df_with_pos_in_template, df_without_pos_in_template


def split_by_freq(df_repetitive_issues: pd.DataFrame,
                  freq_to_separate_template_issues: float,
                  freq_to_separate_rare_and_common_issues: float) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """ Split issues to group according to their frequency. """

    df_template_issues = df_repetitive_issues.loc[
        df_repetitive_issues[TemplateColumns.FREQUENCY.value] > freq_to_separate_template_issues]
    df_typical_issues = df_repetitive_issues.loc[
        df_repetitive_issues[TemplateColumns.FREQUENCY.value] <= freq_to_separate_template_issues]
    df_rare_typical_issues = df_typical_issues.loc[
        df_typical_issues[TemplateColumns.FREQUENCY.value] <= freq_to_separate_rare_and_common_issues]
    df_common_typical_issues = df_typical_issues.loc[
        (df_typical_issues[TemplateColumns.FREQUENCY.value] > freq_to_separate_rare_and_common_issues)]

    return df_template_issues, df_rare_typical_issues, df_common_typical_issues


def filter_by_freq(df_repetitive_issues: pd.DataFrame, freq_to_remove: float) -> pd.DataFrame:
    """ Filter issues with frequency lower or equal to freq_to_remove. """

    return df_repetitive_issues.loc[df_repetitive_issues[TemplateColumns.FREQUENCY.value] > freq_to_remove]


def save_submission_samples(df_repetitive_issues: pd.DataFrame,
                            df_submissions: pd.DataFrame,
                            config: ProcessingConfig):
    sample_path = Path(config.result_path) / 'samples'
    for _, repetitive_issue in df_repetitive_issues.iterrows():
        issue_name = repetitive_issue[IssuesColumns.NAME.value]
        issue_position = repetitive_issue[TemplateColumns.POS_IN_TEMPLATE.value]
        issue_line_number = None if pd.isna(issue_position) else issue_position + 1

        submission_group_ids = ast.literal_eval(repetitive_issue[TemplateColumns.GROUPS.value])

        for group_id in submission_group_ids[:config.solutions_number]:
            submission_series = df_submissions[df_submissions[SubmissionColumns.GROUP.value] == group_id]
            for _, submission in submission_series.iterrows():
                submission_with_issue = submission.copy()
                submission_with_issue[SubmissionColumns.CODE.value] = get_code_with_issue_comment(
                    submission, config.issues_column,
                    issue_name=issue_name,
                    issue_line_number=issue_line_number)

                step_id = submission[SubmissionColumns.STEP_ID.value]
                attempt = submission[SubmissionColumns.ATTEMPT.value]
                submission_path = sample_path / str(step_id) / issue_name / str(group_id)
                save_solution_to_file(submission_with_issue, submission_path, f'attempt_{attempt}')


def add_additional_info(
        df_repetitive_issues: pd.DataFrame,
        config: ProcessingConfig,
        df_submissions: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """ Add urls to steps in repetitive issues dataframe and save samples of repetitive issues occurrence. """

    df_repetitive_issues[StepColumns.URL.value] = df_repetitive_issues[SubmissionColumns.STEP_ID.value] \
        .apply(lambda step_id: f'{config.base_task_url}/{step_id}')
    if df_submissions is not None:
        save_submission_samples(df_repetitive_issues, df_submissions, config)
    df_repetitive_issues = df_repetitive_issues.sort_values(SubmissionColumns.STEP_ID.value)
    return df_repetitive_issues


def process_repetitive_issues(df_repetitive_issues: pd.DataFrame,
                              df_submissions: pd.DataFrame,
                              config: ProcessingConfig) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """ Postprocess given dataframe with repetitive issues for detecting template and typical issues. """
    df_repetitive_issues = filter_by_freq(df_repetitive_issues, config.freq_to_remove)
    if config.with_additional_info:
        df_repetitive_issues = add_additional_info(df_repetitive_issues, df_submissions=df_submissions, config=config)
    df_repetitive_issues_split = split_by_freq(df_repetitive_issues,
                                               config.freq_to_separate_template_issues,
                                               config.freq_to_separate_rare_and_common_issues)
    return df_repetitive_issues_split


def main(config: ProcessingConfig):
    df_repetitive_issues = read_df(config.repetitive_issues_path)
    df_submissions = read_df(config.submissions_path)

    df_template_issues, df_rare_typical_issues, df_common_typical_issues = \
        process_repetitive_issues(df_repetitive_issues, df_submissions, config)

    if config.result_path is None:
        print(df_template_issues)
        print(df_rare_typical_issues)
        print(df_common_typical_issues)
    else:
        base_path = Path(config.result_path) / 'issues'
        create_directory(base_path)
        write_df(df_template_issues, base_path / f'template_issues{AnalysisExtension.CSV.value}')
        write_df(df_rare_typical_issues, base_path / f'rare_typical_issues{AnalysisExtension.CSV.value}')
        write_df(df_common_typical_issues, base_path / f'common_typical_issues{AnalysisExtension.CSV.value}')


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('repetitive_issues_path', type=str,
                        help='Path to .csv file with repetitive issues from submissions.')
    parser.add_argument('submissions_path', type=str, default=None,
                        help='Path to .csv file with submissions with issues.')
    parser.add_argument('issues_column', type=str, default=None,
                        help='Column where issues stored.',
                        choices=[SubmissionColumns.HYPERSTYLE_ISSUES.value, SubmissionColumns.QODANA_ISSUES.value])
    parser.add_argument(
        '--output-path', type=str, default=None,
        help='Path to resulting folder with processed issues. '
             'If no value was passed, the output will be printed into the console.'
    )
    parser.add_argument('-fr', '--freq-to-remove', type=int, default=10,
                        help='The threshold of frequency to remove issues in the final table.')
    parser.add_argument('-fs', '--freq-to-separate-rare-and-common-issues', type=int, default=25,
                        help='The threshold of frequency to separate typical issues into rare and common.')
    parser.add_argument('-ft', '--freq-to-separate-template-issues', type=int, default=51,
                        help='The threshold of frequency to keep issues in the final table.')
    parser.add_argument('--with-additional-info', action='store_true',
                        help='Generate samples with repetitive issues and add urls to steps.')
    parser.add_argument('-n', '--solutions-number', type=int, default=5,
                        help='Tne number of random students solutions that should be gathered for each task.')
    parser.add_argument('-url', '--base-task-url', type=str, default='https://hyperskill.org/learn/step',
                        help='Base url to the tasks on an education platform.')
    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args(sys.argv[1:])
    if args.output_path is None:
        log_file_suffix = Path(args.submissions_path).parent
    else:
        log_file_suffix = args.output_path
    configure_logger(log_file_suffix, 'repetitive_issues_postprocess', args.log_path)

    main(ProcessingConfig.parse_from_args(args))
