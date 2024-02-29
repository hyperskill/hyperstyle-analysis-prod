import argparse
from pathlib import Path
from typing import Dict

import pandas as pd

from core.src.utils.df_utils import read_df, write_df

USER_COLUMN = "user"
ID_COLUMN = "id"
IDX_COLUMN = "id_x"
EMAIL_COLUMN = "email"
RESEARCH_ID_COLUMN = "research_id"
DF_IN_EDU_FILENAME = 'df_in_edu.csv'
DF_NOT_IN_EDU_FILENAME = 'df_not_in_edu.csv'


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        'filtered_data',
        type=lambda value: Path(value).absolute(),
        help='Path to the data filtered by tasktracker_task_filter',
    )

    parser.add_argument(
        'destination_path',
        type=lambda value: Path(value).absolute(),
        help='Path of the directory to save divided data',
    )

    parser.add_argument(
        'users_file',
        type=lambda value: Path(value).absolute(),
        help='Tasktracker users.csv file',
    )

    parser.add_argument(
        'researches_file',
        type=lambda value: Path(value).absolute(),
        help='Tasktracker researches.csv file',
    )

    parser.add_argument(
        'edu_file',
        type=lambda value: Path(value).absolute(),
        help='Edu csv file',
    )


def research_to_email(users_path: Path, researches_path: Path) -> Dict[str, str]:
    users = read_df(users_path)
    researches = read_df(researches_path)
    return pd.merge(researches, users, left_on=USER_COLUMN, right_on=ID_COLUMN, how="left").set_index(IDX_COLUMN)[
        EMAIL_COLUMN].to_dict()


def split_dataframe(filtered_df: pd.DataFrame, edu_df: pd.DataFrame, res_to_email: Dict[str, str]) -> (   # noqa: WPS320
        pd.DataFrame, pd.DataFrame):
    filtered_df[EMAIL_COLUMN] = filtered_df[RESEARCH_ID_COLUMN].map(res_to_email)
    edu_emails = edu_df[EMAIL_COLUMN].unique()
    df_in_edu = filtered_df[filtered_df[EMAIL_COLUMN].isin(edu_emails)]
    df_not_in_edu = filtered_df[~filtered_df[EMAIL_COLUMN].isin(edu_emails)]
    return df_in_edu, df_not_in_edu


def validate(filtered_data: Path, edu_file: Path, destination_path: Path, res_to_email: Dict[str, str]) -> None:
    filtered_df = read_df(filtered_data)
    edu_df = read_df(edu_file)
    df_in_edu, df_not_in_edu = split_dataframe(filtered_df, edu_df, res_to_email)
    write_df(df_in_edu, destination_path / DF_IN_EDU_FILENAME)
    write_df(df_not_in_edu, destination_path / DF_NOT_IN_EDU_FILENAME)


def main():
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args()
    res_to_email = research_to_email(args.users_file, args.researches_file)
    validate(args.filtered_data, args.edu_file, args.destination_path, res_to_email)


if __name__ == '__main__':
    main()
