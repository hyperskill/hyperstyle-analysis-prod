import re
from pathlib import Path
from typing import List

import pandas as pd
from bs4 import BeautifulSoup, Tag

from jba.src.models.edu_logs import TestData, TestDataField, ExceptionData, TestResult

EXCEPTION_REGEXP = re.compile(r'^e: (.*): \((\d+), (\d+)\): (.*)$')
PARAMETRIZED_TEST = re.compile(r'^\[(\d+)] (.*)$', re.DOTALL)
PARAMETRIZED_METHOD_NAME = re.compile(r'(.*)\[(\d+)]')


def _parse_gradle_test_table(html_table: Tag) -> pd.DataFrame:
    header_row = html_table.find('thead').find('tr')
    test_table_header = [column.text.lower().replace(' ', '_') for column in header_row.find_all('th')]

    test_table_data = []
    for row in html_table.find_all('tr'):
        row_data = [column.text for column in row.find_all('td')]
        if row_data:
            test_table_data.append(row_data)

    return pd.DataFrame(test_table_data, columns=test_table_header)


def parse_gradle_test_logs(test_logs_path: Path) -> List[TestData]:
    """
    Parse gradle test logs into list of `TestData`.

    :param test_logs_path: Path to an HTML file with gradle test logs.
    :return: List of `TestData`.
    """
    with open(test_logs_path) as file:
        logs = file.read()

    soup = BeautifulSoup(logs, 'html.parser')

    # Find a tab with failed tests
    failed_test_tab = soup.find('ul', {'class': 'tabLinks'}).find(
        lambda tag: tag.name == 'a' and 'Failed tests' in tag.text
    )

    failed_tests = {}
    if failed_test_tab:
        failed_test_tab_id = failed_test_tab['href'].removeprefix('#')

        for failed_test in soup.find('div', {'id': failed_test_tab_id}).find_all('div', {'class': 'test'}):
            method_name = failed_test.find('a')['name']
            logs = failed_test.find('span', {'class': 'code'}).text

            delimiter_index = logs.find(':')
            error_class = logs[:delimiter_index].strip()
            message = logs[delimiter_index + 1 : logs.find('\tat ')].strip()

            failed_tests[method_name] = {
                TestDataField.ERROR_CLASS.value: error_class,
                TestDataField.MESSAGE.value: message,
            }

    # Find id of a tab with all tests
    test_table_tab_id = (
        soup.find('ul', {'class': 'tabLinks'})
        .find(lambda tag: tag.name == 'a' and "Tests" in tag.text)['href']
        .removeprefix('#')
    )

    test_table = _parse_gradle_test_table(soup.find('div', {'id': test_table_tab_id}).find('table'))

    breadcrumbs = soup.find('div', {'class': 'breadcrumbs'})
    class_name = breadcrumbs.text.split(' > ')[-1].strip()

    tests = []
    for row in test_table.itertuples():
        test = getattr(row, TestDataField.TEST.value)
        raw_method_name = getattr(row, TestDataField.METHOD_NAME.value, test)

        method_name = raw_method_name
        test_number = None
        parametrized_test_match = re.match(PARAMETRIZED_TEST, test)
        if parametrized_test_match is not None:
            test_number = int(parametrized_test_match.group(1))
            test = parametrized_test_match.group(2)
            method_name = re.match(PARAMETRIZED_METHOD_NAME, raw_method_name).group(1)

        tests.append(
            TestData(
                class_name=class_name,
                test=test,
                method_name=method_name,
                duration=getattr(row, TestDataField.DURATION.value),
                result=TestResult(getattr(row, TestDataField.RESULT.value)),
                test_number=test_number,
                error_class=(failed_tests.get(raw_method_name, {}).get(TestDataField.ERROR_CLASS.value)),
                message=failed_tests.get(raw_method_name, {}).get(TestDataField.MESSAGE.value),
            )
        )

    return tests


def parse_gradle_stderr_logs(stderr_logs_path: Path, relative_task_path: str) -> List[ExceptionData]:
    """
    Parse gradle stderr logs into list of `ExceptionData`.

    :param stderr_logs_path: Path to a text file with gradle stderr logs.
    :param relative_task_path: Relative path from a course root to a task folder.
    :return: List of `ExceptionData`.
    """

    exceptions = []
    with open(stderr_logs_path) as file:
        for line in file:
            match = re.match(EXCEPTION_REGEXP, line)
            if not match:
                continue

            full_file_path = match.group(1)
            relative_file_path = full_file_path[full_file_path.find(relative_task_path) + len(relative_task_path) + 1:]

            exceptions.append(
                ExceptionData(
                    path=relative_file_path,
                    line_number=int(match.group(2)),
                    column_number=int(match.group(3)),
                    message=match.group(4),
                ),
            )

    return exceptions
