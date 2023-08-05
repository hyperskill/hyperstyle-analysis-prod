import argparse
import json
import logging
import os
import pandas as pd
from dataclasses import asdict
from pathlib import Path
from typing import Optional, List, Tuple

from core.utils.df_utils import read_df, write_df
from core.utils.file.file_utils import get_output_path
from jba.models.edu_columns import EduColumnName
from jba.models.edu_logs import ExceptionData, TestData
from jba.test_logs.parsers import parse_gradle_test_logs, parse_gradle_stderr_logs
from jba.test_logs.tests_runner import GRADLE_STDERR_LOGS_FILE, TEST_LOGS_FOLDER_NAME

logger = logging.getLogger(__name__)


def parse_gradle_logs(submission: pd.Series, gradle_logs_folder: Path) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse gradle stderr and test logs.

    :param submission: User's submission data.
    :param gradle_logs_folder: Path to a folder with gradle logs.
    :return: Parsed stderr and test logs as json strings.
    """
    submission_id = submission[EduColumnName.ID.value]

    logger.info(f'Parsing submission#{submission_id}')

    submission_gradle_logs_folder = gradle_logs_folder / str(submission_id)
    if not submission_gradle_logs_folder.exists():
        logger.warning("Submission Gradle logs are missing")
        return None, None

    section_name = submission.get(EduColumnName.SECTION_NAME.value)
    lesson_name = submission[EduColumnName.LESSON_NAME.value]
    task_name = submission[EduColumnName.TASK_NAME.value]

    relative_task_path = Path('' if section_name is None else section_name) / lesson_name / task_name

    parsed_stderr_logs = _parse_stderr_logs(submission_gradle_logs_folder, str(relative_task_path))
    if parsed_stderr_logs is not None:
        parsed_stderr_logs = json.dumps([asdict(exception) for exception in parsed_stderr_logs])

    parsed_test_logs = _parse_test_logs(submission_gradle_logs_folder)
    if parsed_test_logs is not None:
        parsed_test_logs = json.dumps([asdict(test) for test in parsed_test_logs])

    return parsed_stderr_logs, parsed_test_logs


def _parse_stderr_logs(submission_gradle_logs_path: Path, relative_task_path: str) -> Optional[List[ExceptionData]]:
    """
    Parse submission gradle stderr logs into list of `ExceptionData`.

    :param submission_gradle_logs_path: Path to a folder with submission gradle logs.
    :param relative_task_path: Relative path from a course root to a task.
    :return: List of `ExceptionData`.
    """
    logger.info('Parsing stderr logs')

    stderr_logs_file = submission_gradle_logs_path / GRADLE_STDERR_LOGS_FILE
    if not stderr_logs_file.exists():
        logger.info('Stderr logs file does not exist')
        return None

    exceptions = parse_gradle_stderr_logs(stderr_logs_file, relative_task_path)
    if not exceptions:
        logger.info('There are no exceptions in the stderr logs file')

    return exceptions


def _parse_test_logs(submission_gradle_logs_path: Path) -> Optional[List[TestData]]:
    """
    Parse submission gradle test logs into list of `TestData`.

    :param submission_gradle_logs_path: Path to a folder with submission gradle logs.
    :return: List of `TestData`.
    """
    logger.info('Parsing test logs')

    test_gradle_logs_path = submission_gradle_logs_path / TEST_LOGS_FOLDER_NAME / 'classes'
    if not test_gradle_logs_path.exists():
        logger.info('Test logs folder does not exist')
        return None

    return [
        test_data
        for test_class_file in os.listdir(test_gradle_logs_path)
        for test_data in parse_gradle_test_logs(test_gradle_logs_path / test_class_file)
    ]


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        'submissions_path',
        type=lambda value: Path(value).absolute(),
        help='Path to .csv file with submissions.',
    )

    parser.add_argument(
        'gradle_logs_path',
        type=lambda value: Path(value).absolute(),
        help='Path to a folder with gradle logs.',
    )

    parser.add_argument(
        '--debug',
        help='Run the script in debug mode.',
        action='store_true',
    )


def main():
    parser = argparse.ArgumentParser()
    configure_parser(parser)
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
    )

    submissions = read_df(args.submissions_path)
    parsed_logs = submissions.apply(
        lambda row: parse_gradle_logs(row, args.gradle_logs_path),
        axis=1,
        result_type='expand',
    ).rename(columns={0: EduColumnName.EXCEPTIONS.value, 1: EduColumnName.TESTS.value})

    submissions_with_parsed_logs = pd.concat([submissions, parsed_logs], axis=1)
    write_df(submissions_with_parsed_logs, get_output_path(args.submissions_path, '-with_parsed_logs'))


if __name__ == '__main__':
    main()
