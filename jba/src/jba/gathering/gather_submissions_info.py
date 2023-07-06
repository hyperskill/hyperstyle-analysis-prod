import argparse
import logging
import os
from typing import List

import pandas as pd
import requests
import sys
from dotenv import load_dotenv

from core.utils.df_utils import filter_df_by_single_value, read_df, write_df
from core.utils.file.file_utils import get_output_path
from core.utils.logging_utils import configure_logger
from jba.models.edu_columns import EduColumnName

logger = logging.getLogger(__name__)


def _get_submissions_by_course_and_user_id(course_id: int, user_id: str) -> pd.DataFrame:
    load_dotenv()
    auth_secret = os.getenv('JBA_API_AUTH_SECRET')
    base_end_point = os.getenv('BASE_END_POINT')
    headers = {"Authorization": f"Bearer {auth_secret}"}

    has_next = True
    page = 0
    submissions_df = []
    logger.info(f'Start getting submissions for course {course_id}, user {user_id}')
    while has_next:
        endpoint = f'{base_end_point}/course/{course_id}/user/{user_id}/submissions/all?page={page}'
        response = requests.get(endpoint, headers=headers)
        if response.status_code != 200:
            logger.error(f'Can not gather submissions for course {course_id}, user {user_id}, and page {page}')
            break
        submissions = response.json()
        submissions_df.append(pd.DataFrame(submissions['submissions']))
        logger.info(f'Page {page} was handled successfully')
        has_next = submissions['has_next']
        page += 1
    logger.info(f'Submissions for course {course_id}, user {user_id} were gathered successfully')
    return pd.concat(submissions_df)


def _get_submissions_by_course_id_and_users(course_id: int, user_ids: List[str]) -> pd.DataFrame:
    submission_dfs = []
    for user_id in user_ids:
        logger.info(f'------------START HANDLING USER {user_id}------------')
        submission_dfs.append(_get_submissions_by_course_and_user_id(course_id, user_id))
        logger.info(f'------------FINISH HANDLING USER {user_id}------------')
    return pd.concat(submission_dfs)


def _get_submission_keys(course_data_df: pd.DataFrame) -> pd.DataFrame:
    submissions_df = []
    course_ids = course_data_df[EduColumnName.COURSE_ID.value].unique()
    for course_id in course_ids:
        logger.info(f'------START HANDLING COURSE {course_id}------')
        user_ids = filter_df_by_single_value(course_data_df, EduColumnName.COURSE_ID.value, course_id)[
            EduColumnName.USER_ID.value].unique()
        submissions_by_course_id_and_users = _get_submissions_by_course_id_and_users(course_id, user_ids)
        submissions_df.append(submissions_by_course_id_and_users)
        logger.info(f'------FINISH HANDLING COURSE {course_id}------')
    return pd.concat(submissions_df)


# TODO: add more arguments
def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('preprocessed_course_data_path', type=str,
                        help='Path to .csv file with preprocessed course data.')
    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args(sys.argv[1:])
    configure_logger(args.preprocessed_course_data_path, 'submissions_info', args.log_path)
    output_path = get_output_path(args.preprocessed_course_data_path, '_submissions_info')
    course_df = read_df(args.preprocessed_course_data_path)
    write_df(_get_submission_keys(course_df), output_path)
