import argparse
import sys

import pandas as pd

from core.src.model.column_name import SubmissionColumns
from core.src.utils.df_utils import read_df, write_df
from core.src.utils.file.file_utils import get_output_path
from core.src.utils.parsing_utils import str_to_datetime
from jba.src.models.edu_columns import EduColumnName


def get_submissions_group(df_submissions: pd.DataFrame) -> pd.DataFrame:
    """ Group submissions by user and step and set submissions from one group same identifier. """

    df_submissions[SubmissionColumns.GROUP.value] = df_submissions \
        .groupby([EduColumnName.USER_ID.value, EduColumnName.TASK_ID.value]).ngroup()

    return df_submissions


def filter_submissions_series(submissions_series: pd.DataFrame) -> pd.DataFrame:
    """ Filter submissions in submission series (group of submissions by one user on one step). """

    submissions_series[EduColumnName.SUBMISSION_DATETIME.value] = \
        submissions_series[EduColumnName.SUBMISSION_DATETIME.value].apply(str_to_datetime)
    submissions_series.sort_values([EduColumnName.SUBMISSION_DATETIME.value], inplace=True)

    group_size = submissions_series.shape[0]
    submissions_series[SubmissionColumns.ATTEMPT.value] = list(range(1, group_size + 1))
    submissions_series[SubmissionColumns.TOTAL_ATTEMPTS.value] = [group_size] * group_size

    return submissions_series


def get_submissions_attempt(df_submissions: pd.DataFrame) -> pd.DataFrame:
    """ Group submissions by user and step and set submissions from one group same identifier. """

    df_submissions = df_submissions \
        .groupby([SubmissionColumns.GROUP.value], as_index=False, group_keys=True) \
        .apply(lambda g: filter_submissions_series(g))

    return df_submissions


# 1. Merge course data with task info
# 2. Add submission group
# 3. Add submission attempt
def preprocess_course_data_and_save(course_data_path: str, course_structure_path: str):
    output_path = get_output_path(course_data_path, '_preprocessed')
    course_data_df = read_df(course_data_path)
    task_info_df = read_df(course_structure_path)
    course_data_df = course_data_df.drop({EduColumnName.TASK_NAME.value}, axis=1)
    df = pd.merge(task_info_df, course_data_df, how='inner', on=EduColumnName.TASK_ID.value)
    # Add submission group
    df = get_submissions_group(df)
    # Add submission attempt
    df = get_submissions_attempt(df)
    write_df(df, output_path)


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('course_data_path', type=str, help='Path to .csv file with course data.')
    parser.add_argument('course_structure_path', type=str, help='Path to .csv with the course structure.')


def main():
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args(sys.argv[1:])
    preprocess_course_data_and_save(args.course_data_path, args.course_structure_path)


if __name__ == '__main__':
    main()
