import json

import argparse
import logging
import pandas as pd
import requests
import sys
from typing import List, Optional

from core.model.column_name import SubmissionColumns
from core.utils.df_utils import filter_df_by_single_value, read_df, write_df
from core.utils.file.file_utils import get_output_path
from core.utils.logging_utils import configure_logger
from jba.gathering.query_info_storage import QueryInfoStorage
from jba.models.edu_columns import EduColumnName

logger = logging.getLogger(__name__)


def _get_submissions_by_course_and_user_id(query_storage_info: QueryInfoStorage,
                                           course_id: int, user_id: str,
                                           to_gather_code: bool = False) -> pd.DataFrame:
    has_next = True
    page = 0
    submissions_dfs = []
    logger.info(f'Start getting submissions for course {course_id}, user {user_id}')
    while has_next:
        endpoint = f'{query_storage_info.base_end_point}/admin/course/{course_id}/user/{user_id}/submissions/all?page={page}'
        response = requests.get(endpoint, headers=query_storage_info.get_auth_headers())
        if response.status_code != 200:
            logger.error(f'Can not gather submissions for course {course_id}, user {user_id}, and page {page}')
            break
        submissions = response.json()
        submissions_df = pd.DataFrame(submissions['submissions'])
        if submissions_df.shape == (0, 0):
            break
        if to_gather_code:
            submissions_df[EduColumnName.CODE_SNIPPETS.value] = submissions_df.apply(
                lambda row: _get_solution_from_s3(query_storage_info, row), axis=1)
        submissions_dfs.append(submissions_df)
        logger.info(f'Page {page} was handled successfully')
        has_next = submissions['has_next']
        page += 1
    logger.info(f'Submissions for course {course_id}, user {user_id} were gathered successfully')
    if len(submissions_dfs) == 0:
        return pd.DataFrame([
            EduColumnName.ID.value,
            EduColumnName.TASK_ID.value,
            EduColumnName.SOLUTION_AWS_KEY.value,
            SubmissionColumns.TIME.value,
            EduColumnName.FORMAT_VERSION.value,
            EduColumnName.UPDATE_VERSION.value,
            EduColumnName.STATUS.value,
            EduColumnName.CHECKER_OUTPUT.value,
            EduColumnName.TASK_TYPE.value,
            EduColumnName.USER_ID.value,
            EduColumnName.UUID.value,
            EduColumnName.VISIBILITY.value,
            EduColumnName.TASK_NAME.value,
            EduColumnName.CODE_SNIPPETS.value,
        ])
    return pd.concat(submissions_dfs)


def _get_solution_from_s3(query_storage_info: QueryInfoStorage, row: pd.DataFrame) -> Optional[str]:
    aws_key = row[EduColumnName.SOLUTION_AWS_KEY.value]
    endpoint = f'{query_storage_info.base_end_point}/solution?solutionKey={aws_key}'
    response = requests.get(endpoint, headers=query_storage_info.get_auth_headers())
    if response.status_code != 200:
        logger.error(f'Can not gather code for aws key: {aws_key}')
        return None
    s3_link = response.content.decode('utf-8')
    solution_response = requests.get(s3_link)
    if solution_response.status_code != 200:
        logger.error(f'Can not gather code for s3 link: {s3_link}')
        return None
    if len(solution_response.content.decode('utf-8')) == 0:
        return ''
    solution = json.dumps(list(map(lambda s: {key: s[key] for key in ['name', 'text']}, solution_response.json())))
    logger.info(f'User solution is {solution}')
    return solution


def _get_submissions_by_course_id_and_users(query_storage_info: QueryInfoStorage, course_id: int, user_ids: List[str],
                                            to_gather_code: bool = False) -> pd.DataFrame:
    submission_dfs = []
    for user_id in user_ids:
        logger.info(f'------------START HANDLING USER {user_id}------------')
        submission_dfs.append(
            _get_submissions_by_course_and_user_id(query_storage_info, course_id, user_id, to_gather_code))
        logger.info(f'------------FINISH HANDLING USER {user_id}------------')
    return pd.concat(submission_dfs)


def _get_submissions(query_storage_info: QueryInfoStorage,
                     course_data_df: pd.DataFrame,
                     to_gather_code: bool = False) -> pd.DataFrame:
    submissions_df = []
    course_ids = course_data_df[EduColumnName.COURSE_ID.value].unique()
    for course_id in course_ids:
        logger.info(f'------START HANDLING COURSE {course_id}------')
        user_ids = filter_df_by_single_value(course_data_df, EduColumnName.COURSE_ID.value, course_id)[
            EduColumnName.USER_ID.value].unique()
        submissions_by_course_id_and_users = \
            _get_submissions_by_course_id_and_users(query_storage_info, course_id, user_ids, to_gather_code)
        submissions_df.append(submissions_by_course_id_and_users)
        logger.info(f'------FINISH HANDLING COURSE {course_id}------')
    return pd.concat(submissions_df)


# TODO: add more arguments
def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('preprocessed_course_data_path', type=str,
                        help='Path to .csv file with preprocessed course data.')
    parser.add_argument('--log-path', type=str, default=None, help='Path to directory for log.')
    parser.add_argument(
        '--gather-code', action='store_true',
        help='Indicates if you need to download students code.',
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args(sys.argv[1:])
    configure_logger(args.preprocessed_course_data_path, 'submissions_info', args.log_path)
    output_path = get_output_path(args.preprocessed_course_data_path, '_submissions_info')
    course_df = read_df(args.preprocessed_course_data_path)
    query_storage_info = QueryInfoStorage()
    submissions_df = _get_submissions(query_storage_info, course_df, to_gather_code=args.gather_code)
    write_df(submissions_df, output_path)
