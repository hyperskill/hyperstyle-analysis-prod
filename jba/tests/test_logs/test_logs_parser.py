import shutil
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
import pytest
from pandas._testing import assert_frame_equal

from core.src.utils.subprocess_runner import run_in_subprocess
from jba.src import MAIN_FOLDER
from jba.src.models.edu_columns import EduColumnName
from jba.src.models.edu_logs import ExceptionData, TestData, TestResult
from jba.src.test_logs.logs_parser import _parse_stderr_logs, _parse_test_logs, parse_gradle_logs
from jba.tests.test_logs import TEST_LOGS_FOLDER

LOGS_PARSER_FOLDER = TEST_LOGS_FOLDER / 'logs_parser'


SUBMISSIONS_ID_TO_EXPECTED_EXCEPTIONS = {
    0: None,
    1: None,
    2: [
        ExceptionData(
            path='src/main/kotlin/Main.kt',
            line_number=4,
            column_number=9,
            message='Conflicting declarations: val firstUserAnswer: String, val firstUserAnswer: String',
        ),
        ExceptionData(
            path='src/main/kotlin/Main.kt',
            line_number=5,
            column_number=9,
            message='Conflicting declarations: val secondUserAnswer: String, val secondUserAnswer: String',
        ),
        ExceptionData(
            path='src/main/kotlin/Main.kt',
            line_number=6,
            column_number=9,
            message='Conflicting declarations: val thirdUserAnswer: String, val thirdUserAnswer: String',
        ),
        ExceptionData(
            path='src/main/kotlin/Main.kt',
            line_number=8,
            column_number=9,
            message='Conflicting declarations: val firstUserAnswer: String, val firstUserAnswer: String',
        ),
        ExceptionData(
            path='src/main/kotlin/Main.kt',
            line_number=8,
            column_number=36,
            message='Type mismatch: inferred type is String? but String was expected',
        ),
        ExceptionData(
            path='src/main/kotlin/Main.kt',
            line_number=10,
            column_number=9,
            message='Conflicting declarations: val secondUserAnswer: String, val secondUserAnswer: String',
        ),
        ExceptionData(
            path='src/main/kotlin/Main.kt',
            line_number=10,
            column_number=37,
            message='Type mismatch: inferred type is String? but String was expected',
        ),
        ExceptionData(
            path='src/main/kotlin/Main.kt',
            line_number=12,
            column_number=9,
            message='Conflicting declarations: val thirdUserAnswer: String, val thirdUserAnswer: String',
        ),
        ExceptionData(
            path='src/main/kotlin/Main.kt',
            line_number=12,
            column_number=36,
            message='Type mismatch: inferred type is String? but String was expected',
        ),
    ],
    3: [],
}

SUBMISSIONS_ID_TO_EXPECTED_TEST = {
    0: None,
    1: [
        TestData(
            class_name='Test',
            test='testCountExactMatchesFunction()',
            method_name='testCountExactMatchesFunction()',
            duration='0s',
            result=TestResult.PASSED,
        ),
        TestData(
            class_name='Test',
            test='ABBA, ABCD, 2, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)',
            duration='0.001s',
            result=TestResult.PASSED,
            test_number=10,
        ),
        TestData(
            class_name='Test',
            test='AAAA, ABBB, 1, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)',
            duration='0s',
            result=TestResult.PASSED,
            test_number=11,
        ),
        TestData(
            class_name='Test',
            test='BBBB, BBDH, 2, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)',
            duration='0.001s',
            result=TestResult.PASSED,
            test_number=12,
        ),
        TestData(
            class_name='Test',
            test='AAAA, ABCD, 1, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)',
            duration='0s',
            result=TestResult.PASSED,
            test_number=13,
        ),
        TestData(
            class_name='Test',
            test='ACEB, BCDF, 1, 1',
            method_name='testCountExactMatchesImplementation(String, String, int, int)',
            duration='0.013s',
            result=TestResult.PASSED,
            test_number=1,
        ),
        TestData(
            class_name='Test',
            test='ABCD, ABCD, 4, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)',
            duration='0.001s',
            result=TestResult.PASSED,
            test_number=2,
        ),
        TestData(
            class_name='Test',
            test='ABCD, DCBA, 0, 4',
            method_name='testCountExactMatchesImplementation(String, String, int, int)',
            duration='0.001s',
            result=TestResult.PASSED,
            test_number=3,
        ),
        TestData(
            class_name='Test',
            test='ABCD, DBCA, 2, 2',
            method_name='testCountExactMatchesImplementation(String, String, int, int)',
            duration='0.001s',
            result=TestResult.PASSED,
            test_number=4,
        ),
        TestData(
            class_name='Test',
            test='ABCD, EBCF, 2, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)',
            duration='0.001s',
            result=TestResult.PASSED,
            test_number=5,
        ),
        TestData(
            class_name='Test',
            test='AAAA, AAAA, 4, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)',
            duration='0.001s',
            result=TestResult.PASSED,
            test_number=6,
        ),
        TestData(
            class_name='Test',
            test='AAAA, BBBB, 0, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)',
            duration='0.001s',
            result=TestResult.PASSED,
            test_number=7,
        ),
        TestData(
            class_name='Test',
            test='AABB, BBAA, 0, 4',
            method_name='testCountExactMatchesImplementation(String, String, int, int)',
            duration='0.001s',
            result=TestResult.PASSED,
            test_number=8,
        ),
        TestData(
            class_name='Test',
            test='ABCD, ABBA, 2, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)',
            duration='0s',
            result=TestResult.PASSED,
            test_number=9,
        ),
        TestData(
            class_name='Test',
            test='testCountGenerateSecretFunction()',
            method_name='testCountGenerateSecretFunction()',
            duration='0.001s',
            result=TestResult.PASSED,
        ),
        TestData(
            class_name='Test',
            test='testCountPartialMatchesFunction()',
            method_name='testCountPartialMatchesFunction()',
            duration='0.071s',
            result=TestResult.PASSED,
        ),
        TestData(
            class_name='Test',
            test='ABBA, ABCD, 2, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)',
            duration='0.001s',
            result=TestResult.PASSED,
            test_number=10,
        ),
        TestData(
            class_name='Test',
            test='AAAA, ABBB, 1, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)',
            duration='0s',
            result=TestResult.PASSED,
            test_number=11,
        ),
        TestData(
            class_name='Test',
            test='BBBB, BBDH, 2, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)',
            duration='0.002s',
            result=TestResult.PASSED,
            test_number=12,
        ),
        TestData(
            class_name='Test',
            test='AAAA, ABCD, 1, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)',
            duration='0.006s',
            result=TestResult.PASSED,
            test_number=13,
        ),
        TestData(
            class_name='Test',
            test='ACEB, BCDF, 1, 1',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)',
            duration='0.001s',
            result=TestResult.PASSED,
            test_number=1,
        ),
        TestData(
            class_name='Test',
            test='ABCD, ABCD, 4, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)',
            duration='0.001s',
            result=TestResult.PASSED,
            test_number=2,
        ),
        TestData(
            class_name='Test',
            test='ABCD, DCBA, 0, 4',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)',
            duration='0s',
            result=TestResult.PASSED,
            test_number=3,
        ),
        TestData(
            class_name='Test',
            test='ABCD, DBCA, 2, 2',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)',
            duration='0s',
            result=TestResult.PASSED,
            test_number=4,
        ),
        TestData(
            class_name='Test',
            test='ABCD, EBCF, 2, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)',
            duration='0.004s',
            result=TestResult.PASSED,
            test_number=5,
        ),
        TestData(
            class_name='Test',
            test='AAAA, AAAA, 4, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)',
            duration='0.001s',
            result=TestResult.PASSED,
            test_number=6,
        ),
        TestData(
            class_name='Test',
            test='AAAA, BBBB, 0, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)',
            duration='0s',
            result=TestResult.PASSED,
            test_number=7,
        ),
        TestData(
            class_name='Test',
            test='AABB, BBAA, 0, 4',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)',
            duration='0s',
            result=TestResult.PASSED,
            test_number=8,
        ),
        TestData(
            class_name='Test',
            test='ABCD, ABBA, 2, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)',
            duration='0s',
            result=TestResult.PASSED,
            test_number=9,
        ),
        TestData(
            class_name='Test',
            test='testGetGameRulesFunction()',
            method_name='testGetGameRulesFunction()',
            duration='0.001s',
            result=TestResult.PASSED,
        ),
        TestData(
            class_name='Test',
            test='testIsCompleteFunction()',
            method_name='testIsCompleteFunction()',
            duration='0s',
            result=TestResult.PASSED,
        ),
        TestData(
            class_name='Test',
            test='ACEB, BCDF, false',
            method_name='testIsCompleteImplementation(String, String, boolean)',
            duration='0.003s',
            result=TestResult.PASSED,
            test_number=1,
        ),
        TestData(
            class_name='Test',
            test='ACEB, ACEB, true',
            method_name='testIsCompleteImplementation(String, String, boolean)',
            duration='0s',
            result=TestResult.PASSED,
            test_number=2,
        ),
        TestData(
            class_name='Test',
            test='testSolution()',
            method_name='testSolution()',
            duration='0.016s',
            result=TestResult.PASSED,
        ),
    ],
    2: None,
    3: [
        TestData(
            class_name='Test',
            test='testCountExactMatchesFunction()',
            method_name='testCountExactMatchesFunction()',
            duration='0s',
            result=TestResult.PASSED,
        ),
        TestData(
            class_name='Test',
            test='ABBA, ABCD, 2, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)',
            duration='0.001s',
            result=TestResult.PASSED,
            test_number=10,
        ),
        TestData(
            class_name='Test',
            test='AAAA, ABBB, 1, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)',
            duration='0.001s',
            result=TestResult.PASSED,
            test_number=11,
        ),
        TestData(
            class_name='Test',
            test='BBBB, BBDH, 2, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)',
            duration='0s',
            result=TestResult.PASSED,
            test_number=12,
        ),
        TestData(
            class_name='Test',
            test='AAAA, ABCD, 1, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)',
            duration='0s',
            result=TestResult.PASSED,
            test_number=13,
        ),
        TestData(
            class_name='Test',
            test='ACEB, BCDF, 1, 1',
            method_name='testCountExactMatchesImplementation(String, String, int, int)',
            duration='0.012s',
            result=TestResult.PASSED,
            test_number=1,
        ),
        TestData(
            class_name='Test',
            test='ABCD, ABCD, 4, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)',
            duration='0.001s',
            result=TestResult.PASSED,
            test_number=2,
        ),
        TestData(
            class_name='Test',
            test='ABCD, DCBA, 0, 4',
            method_name='testCountExactMatchesImplementation(String, String, int, int)',
            duration='0.001s',
            result=TestResult.PASSED,
            test_number=3,
        ),
        TestData(
            class_name='Test',
            test='ABCD, DBCA, 2, 2',
            method_name='testCountExactMatchesImplementation(String, String, int, int)',
            duration='0s',
            result=TestResult.PASSED,
            test_number=4,
        ),
        TestData(
            class_name='Test',
            test='ABCD, EBCF, 2, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)',
            duration='0s',
            result=TestResult.PASSED,
            test_number=5,
        ),
        TestData(
            class_name='Test',
            test='AAAA, AAAA, 4, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)',
            duration='0s',
            result=TestResult.PASSED,
            test_number=6,
        ),
        TestData(
            class_name='Test',
            test='AAAA, BBBB, 0, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)',
            duration='0s',
            result=TestResult.PASSED,
            test_number=7,
        ),
        TestData(
            class_name='Test',
            test='AABB, BBAA, 0, 4',
            method_name='testCountExactMatchesImplementation(String, String, int, int)',
            duration='0s',
            result=TestResult.PASSED,
            test_number=8,
        ),
        TestData(
            class_name='Test',
            test='ABCD, ABBA, 2, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)',
            duration='0s',
            result=TestResult.PASSED,
            test_number=9,
        ),
        TestData(
            class_name='Test',
            test='testCountGenerateSecretFunction()',
            method_name='testCountGenerateSecretFunction()',
            duration='0.001s',
            result=TestResult.PASSED,
        ),
        TestData(
            class_name='Test',
            test='testCountPartialMatchesFunction()',
            method_name='testCountPartialMatchesFunction()',
            duration='0.021s',
            result=TestResult.PASSED,
        ),
        TestData(
            class_name='Test',
            test='ABBA, ABCD, 2, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)',
            duration='0.001s',
            result=TestResult.FAILED,
            test_number=10,
            error_class='java.lang.StringIndexOutOfBoundsException',
            message='Index 4 out of bounds for length 4',
        ),
        TestData(
            class_name='Test',
            test='AAAA, ABBB, 1, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)',
            duration='0.001s',
            result=TestResult.FAILED,
            test_number=11,
            error_class='java.lang.StringIndexOutOfBoundsException',
            message='Index 4 out of bounds for length 4',
        ),
        TestData(
            class_name='Test',
            test='BBBB, BBDH, 2, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)',
            duration='0.001s',
            result=TestResult.FAILED,
            test_number=12,
            error_class='java.lang.StringIndexOutOfBoundsException',
            message='Index 4 out of bounds for length 4',
        ),
        TestData(
            class_name='Test',
            test='AAAA, ABCD, 1, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)',
            duration='0.001s',
            result=TestResult.FAILED,
            test_number=13,
            error_class='java.lang.StringIndexOutOfBoundsException',
            message='Index 4 out of bounds for length 4',
        ),
        TestData(
            class_name='Test',
            test='ACEB, BCDF, 1, 1',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)',
            duration='0.003s',
            result=TestResult.FAILED,
            test_number=1,
            error_class='java.lang.StringIndexOutOfBoundsException',
            message='Index 4 out of bounds for length 4',
        ),
        TestData(
            class_name='Test',
            test='ABCD, ABCD, 4, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)',
            duration='0s',
            result=TestResult.FAILED,
            test_number=2,
            error_class='java.lang.StringIndexOutOfBoundsException',
            message='Index 4 out of bounds for length 4',
        ),
        TestData(
            class_name='Test',
            test='ABCD, DCBA, 0, 4',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)',
            duration='0.001s',
            result=TestResult.FAILED,
            test_number=3,
            error_class='java.lang.StringIndexOutOfBoundsException',
            message='Index 4 out of bounds for length 4',
        ),
        TestData(
            class_name='Test',
            test='ABCD, DBCA, 2, 2',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)',
            duration='0.001s',
            result=TestResult.FAILED,
            test_number=4,
            error_class='java.lang.StringIndexOutOfBoundsException',
            message='Index 4 out of bounds for length 4',
        ),
        TestData(
            class_name='Test',
            test='ABCD, EBCF, 2, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)',
            duration='0s',
            result=TestResult.FAILED,
            test_number=5,
            error_class='java.lang.StringIndexOutOfBoundsException',
            message='Index 4 out of bounds for length 4',
        ),
        TestData(
            class_name='Test',
            test='AAAA, AAAA, 4, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)',
            duration='0s',
            result=TestResult.FAILED,
            test_number=6,
            error_class='java.lang.StringIndexOutOfBoundsException',
            message='Index 4 out of bounds for length 4',
        ),
        TestData(
            class_name='Test',
            test='AAAA, BBBB, 0, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)',
            duration='0.001s',
            result=TestResult.FAILED,
            test_number=7,
            error_class='java.lang.StringIndexOutOfBoundsException',
            message='Index 4 out of bounds for length 4',
        ),
        TestData(
            class_name='Test',
            test='AABB, BBAA, 0, 4',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)',
            duration='0.001s',
            result=TestResult.FAILED,
            test_number=8,
            error_class='java.lang.StringIndexOutOfBoundsException',
            message='Index 4 out of bounds for length 4',
        ),
        TestData(
            class_name='Test',
            test='ABCD, ABBA, 2, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)',
            duration='0.001s',
            result=TestResult.FAILED,
            test_number=9,
            error_class='java.lang.StringIndexOutOfBoundsException',
            message='Index 4 out of bounds for length 4',
        ),
        TestData(
            class_name='Test',
            test='testGetGameRulesFunction()',
            method_name='testGetGameRulesFunction()',
            duration='0s',
            result=TestResult.PASSED,
        ),
        TestData(
            class_name='Test',
            test='testIsCompleteFunction()',
            method_name='testIsCompleteFunction()',
            duration='0.001s',
            result=TestResult.PASSED,
        ),
        TestData(
            class_name='Test',
            test='ACEB, BCDF, false',
            method_name='testIsCompleteImplementation(String, String, boolean)',
            duration='0.003s',
            result=TestResult.PASSED,
            test_number=1,
        ),
        TestData(
            class_name='Test',
            test='ACEB, ACEB, true',
            method_name='testIsCompleteImplementation(String, String, boolean)',
            duration='0s',
            result=TestResult.PASSED,
            test_number=2,
        ),
        TestData(
            class_name='Test',
            test='testSolution()',
            method_name='testSolution()',
            duration='0.012s',
            result=TestResult.PASSED,
        ),
    ],
}


PARSE_STDERR_LOGS_DATA = [
    (0, 'there/is/no/task'),
    (1, 'Introduction/WarmUp/CollectionsPartTwo'),
    (2, 'Introduction/TheFirstDateWithProgramming/ReadUserInput'),
    (3, 'Introduction/WarmUp/CollectionsPartTwo'),
]


@pytest.mark.parametrize(('submission_id', 'task_path'), PARSE_STDERR_LOGS_DATA)
def test_parse_stderr_logs(submission_id: int, task_path: str):
    assert (
        _parse_stderr_logs(LOGS_PARSER_FOLDER / 'gradle_logs' / str(submission_id), task_path)
        == SUBMISSIONS_ID_TO_EXPECTED_EXCEPTIONS[submission_id]
    )


@pytest.mark.parametrize('submission_id', range(4))
def test_parse_test_logs(submission_id: int):
    assert (
        _parse_test_logs(LOGS_PARSER_FOLDER / 'gradle_logs' / str(submission_id))
        == SUBMISSIONS_ID_TO_EXPECTED_TEST[submission_id]
    )


@pytest.mark.parametrize('submission_id', range(4))
def test_parse_gradle_logs(submission_id: int):
    submissions = pd.read_csv(LOGS_PARSER_FOLDER / 'submissions.csv')

    actual_parsed_logs = parse_gradle_logs(
        submissions[submissions[EduColumnName.ID.value] == submission_id].squeeze(), LOGS_PARSER_FOLDER / 'gradle_logs'
    )

    actual_exceptions, actual_tests = actual_parsed_logs
    actual_exceptions = (
        None if actual_exceptions is None else ExceptionData.schema().loads(actual_exceptions, many=True)
    )
    actual_tests = None if actual_tests is None else TestData.schema().loads(actual_tests, many=True)

    expected_exceptions = SUBMISSIONS_ID_TO_EXPECTED_EXCEPTIONS[submission_id]
    expected_tests = SUBMISSIONS_ID_TO_EXPECTED_TEST[submission_id]

    assert actual_exceptions == expected_exceptions
    assert actual_tests == expected_tests


def test_functional():
    with TemporaryDirectory() as tmp_dir:
        shutil.copyfile(LOGS_PARSER_FOLDER / 'submissions.csv', Path(tmp_dir) / 'submissions.csv')

        command = [
            sys.executable,
            (MAIN_FOLDER.parent / 'test_logs' / 'logs_parser.py'),
            (Path(tmp_dir) / 'submissions.csv'),
            (LOGS_PARSER_FOLDER / 'gradle_logs'),
        ]

        run_in_subprocess(command)

        actual_submissions = pd.read_csv(Path(tmp_dir) / 'submissions-with_parsed_logs.csv')
        expected_submissions = pd.read_csv(LOGS_PARSER_FOLDER / 'submissions-with_parsed_logs.csv')

        for actual_row, expected_row in zip(actual_submissions.itertuples(), expected_submissions.itertuples()):
            actual_tests = (
                None
                if pd.isna(getattr(actual_row, EduColumnName.TESTS.value))
                else TestData.schema().loads(getattr(actual_row, EduColumnName.TESTS.value), many=True)
            )

            expected_tests = (
                None
                if pd.isna(getattr(expected_row, EduColumnName.TESTS.value))
                else TestData.schema().loads(getattr(expected_row, EduColumnName.TESTS.value), many=True)
            )

            assert actual_tests == expected_tests

            actual_exceptions = (
                None
                if pd.isna(getattr(actual_row, EduColumnName.EXCEPTIONS.value))
                else ExceptionData.schema().loads(getattr(actual_row, EduColumnName.EXCEPTIONS.value), many=True)
            )

            expected_exceptions = (
                None
                if pd.isna(getattr(expected_row, EduColumnName.EXCEPTIONS.value))
                else ExceptionData.schema().loads(getattr(expected_row, EduColumnName.EXCEPTIONS.value), many=True)
            )

            assert actual_exceptions == expected_exceptions

        actual_submissions_without_parsed_logs = actual_submissions.drop(
            columns=[EduColumnName.EXCEPTIONS.value, EduColumnName.TESTS.value],
        )

        expected_submissions_without_parsed_logs = expected_submissions.drop(
            columns=[EduColumnName.EXCEPTIONS.value, EduColumnName.TESTS.value],
        )

        # Asserting that other columns didn't change
        assert_frame_equal(actual_submissions_without_parsed_logs, expected_submissions_without_parsed_logs)


def test_functional_incorrect_arguments():
    command = [sys.executable, (MAIN_FOLDER.parent / 'test_logs' / 'logs_parser.py')]

    stdout, stderr = run_in_subprocess(command)

    assert stdout == ''
    assert 'error: the following arguments are required' in stderr
