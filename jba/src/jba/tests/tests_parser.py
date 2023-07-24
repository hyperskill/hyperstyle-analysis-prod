from enum import Enum, unique

import argparse
import json
import logging
import os
import pandas as pd
import re
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, List, Tuple

from core.utils.df_utils import read_df, write_df
from core.utils.file.file_utils import get_output_path, get_name_from_path
from jba.models.edu_columns import EduColumnName
from jba.tests.tests_runner import GRADLE_STDERR_LOGS_FILE, TEST_LOGS_FOLDER_NAME

logger = logging.getLogger(__name__)

EXCEPTION_REGEXP = re.compile(r'^e: (.*): \((\d+), (\d+)\): (.*)$')


@unique
class TestDataField(Enum):
    CLASS_NAME = 'class_name'
    TEST = 'test'
    METHOD_NAME = 'method_name'
    DURATION = 'duration'
    RESULT = 'result'
    ERROR_CLASS = 'error_class'
    MESSAGE = 'message'


@dataclass
class TestData:
    class_name: str
    test: str
    method_name: str
    duration: str
    result: str

    error_class: Optional[str] = None
    message: Optional[str] = None


@dataclass
class ExceptionData:
    path: str
    line_number: int
    column_number: int
    message: str


def parse_gradle_logs(submission: pd.Series, gradle_logs_path: Path) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse Gradle stderr and test logs.

    :param submission: User's submission data.
    :param gradle_logs_path: Path to a folder with gradle logs.
    :return: Parsed stderr and test logs as json strings.
    """
    submission_id = submission[EduColumnName.ID.value]

    logger.info(f'Parsing submission#{submission_id}')

    submission_gradle_logs_path = gradle_logs_path / str(submission_id)
    if not submission_gradle_logs_path.exists():
        logger.warning("Submission Gradle logs are missing")
        return None, None

    section_name = submission.get(EduColumnName.SECTION_NAME.value)
    lesson_name = submission[EduColumnName.LESSON_NAME.value]
    task_name = submission[EduColumnName.TASK_NAME.value]

    task_path = Path('' if section_name is None else section_name) / lesson_name / task_name

    parsed_stderr_logs = _parse_stderr_logs(str(task_path), submission_gradle_logs_path)
    if parsed_stderr_logs:
        parsed_stderr_logs = json.dumps([asdict(exception) for exception in parsed_stderr_logs])

    parsed_test_logs = _parse_test_logs(submission_gradle_logs_path)
    if parsed_test_logs:
        parsed_test_logs = json.dumps([asdict(test) for test in parsed_test_logs])

    return parsed_stderr_logs, parsed_test_logs


def _parse_stderr_logs(task_path: str, submission_gradle_logs_path: Path) -> Optional[List[ExceptionData]]:
    """
    Parse Gradle stderr logs into list of `ExceptionData`.

    :param task_path: Relative path from a course root to a task.
    :param submission_gradle_logs_path: Path to a file with gradle stderr logs.
    :return: List of `ExceptionData`.
    """
    logger.info('Parsing stderr logs')

    stderr_logs_file = submission_gradle_logs_path / GRADLE_STDERR_LOGS_FILE
    if not stderr_logs_file.exists():
        logger.info('Stderr logs file does not exist')
        return None

    exceptions = []
    with open(stderr_logs_file) as file:
        for line in file:
            match = re.match(EXCEPTION_REGEXP, line)
            if not match:
                continue

            full_file_path = match.group(1)
            relative_file_path = full_file_path[full_file_path.find(task_path) + len(task_path) + 1:]

            exceptions.append(
                ExceptionData(
                    path=relative_file_path,
                    line_number=int(match.group(2)),
                    column_number=int(match.group(3)),
                    message=match.group(4),
                ),
            )

    if not exceptions:
        logger.info('There are no exceptions in the stderr logs file')

    return exceptions


def _parse_test_logs(submission_gradle_logs_path: Path) -> Optional[List[TestData]]:
    """
    Parse Gradle test logs into list of `TestData`.

    :param submission_gradle_logs_path: Path to a file with gradle stderr logs.
    :return: List of `TestData`.
    """
    logger.info('Parsing test logs')

    test_logs_path = submission_gradle_logs_path / TEST_LOGS_FOLDER_NAME / 'classes'
    if not test_logs_path.exists():
        logger.info('Test logs file does not exist')
        return None

    tests = []
    for test_class_file in os.listdir(test_logs_path):
        test_class_logs_path = test_logs_path / test_class_file

        with open(test_class_logs_path) as file:
            logs = file.read()

        soup = BeautifulSoup(logs, 'html.parser')

        # Find a tab with failed tests
        failed_test_tab = soup.find('ul', {'class': 'tabLinks'}).find(
            lambda tag: tag.name == 'a' and 'Failed tests' in tag.text.strip()
        )

        failed_tests = {}
        if failed_test_tab:
            failed_test_tab_id = failed_test_tab['href'].removeprefix('#')

            for failed_test in soup.find('div', {'id': failed_test_tab_id}).find_all('div', {'class': 'test'}):
                test = failed_test.find('h3', {'class': 'failures'}).text.strip()
                logs = failed_test.find('span', {'class': 'code'}).text.strip()

                delimiter_index = logs.find(':')
                error_class = logs[:delimiter_index].strip()
                message = logs[delimiter_index + 1 : logs.find('\tat ')].strip()

                failed_tests[test] = {
                    TestDataField.ERROR_CLASS.value: error_class,
                    TestDataField.MESSAGE.value: message,
                }

        # Find id of a tab with all tests
        test_table_tab_id = (
            soup.find('ul', {'class': 'tabLinks'})
            .find(lambda tag: tag.name == 'a' and "Tests" in tag.text.strip())['href']
            .removeprefix('#')
        )

        test_table = pd.read_html(str(soup.find('div', {'id': test_table_tab_id})))[0]
        test_table.columns = map(lambda name: name.lower().replace(' ', '_'), test_table.columns)

        tests.extend(
            test_table.apply(
                lambda row: TestData(
                    class_name=get_name_from_path(test_class_file, with_extension=False),
                    test=row[TestDataField.TEST.value],
                    method_name=row.get(TestDataField.METHOD_NAME.value, row[TestDataField.TEST.value]),
                    duration=row[TestDataField.DURATION.value],
                    result=row[TestDataField.RESULT.value],
                    error_class=(
                        failed_tests.get(row[TestDataField.TEST.value], {}).get(TestDataField.ERROR_CLASS.value)
                    ),
                    message=failed_tests.get(row[TestDataField.TEST.value], {}).get(TestDataField.MESSAGE.value),
                ),
                axis=1,
            ),
        )

    return tests


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
    ).rename(columns={0: 'exceptions', 1: 'tests'})

    submissions_with_parsed_logs = pd.concat([submissions, parsed_logs], axis=1)
    write_df(submissions_with_parsed_logs, get_output_path(args.submissions_path, '-with_parsed_logs'))


if __name__ == '__main__':
    main()
