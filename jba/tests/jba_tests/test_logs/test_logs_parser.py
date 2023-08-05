import json
import pandas as pd
import pytest
import shutil
import sys
from pandas._testing import assert_frame_equal
from pathlib import Path
from tempfile import TemporaryDirectory

from core.utils.subprocess_runner import run_in_subprocess
from jba import MAIN_FOLDER
from jba.models.edu_columns import EduColumnName
from jba.models.edu_logs import ExceptionData, TestData
from jba.test_logs.logs_parser import _parse_stderr_logs, _parse_test_logs, parse_gradle_logs
from jba_tests.test_logs import TEST_LOGS_FOLDER

TESTS_PARSER_FOLDER = TEST_LOGS_FOLDER / 'tests_parser'


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
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[10] ABBA, ABCD, 2, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)[10]',
            duration='0.001s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[11] AAAA, ABBB, 1, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)[11]',
            duration='0s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[12] BBBB, BBDH, 2, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)[12]',
            duration='0.001s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[13] AAAA, ABCD, 1, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)[13]',
            duration='0s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[1] ACEB, BCDF, 1, 1',
            method_name='testCountExactMatchesImplementation(String, String, int, int)[1]',
            duration='0.013s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[2] ABCD, ABCD, 4, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)[2]',
            duration='0.001s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[3] ABCD, DCBA, 0, 4',
            method_name='testCountExactMatchesImplementation(String, String, int, int)[3]',
            duration='0.001s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[4] ABCD, DBCA, 2, 2',
            method_name='testCountExactMatchesImplementation(String, String, int, int)[4]',
            duration='0.001s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[5] ABCD, EBCF, 2, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)[5]',
            duration='0.001s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[6] AAAA, AAAA, 4, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)[6]',
            duration='0.001s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[7] AAAA, BBBB, 0, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)[7]',
            duration='0.001s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[8] AABB, BBAA, 0, 4',
            method_name='testCountExactMatchesImplementation(String, String, int, int)[8]',
            duration='0.001s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[9] ABCD, ABBA, 2, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)[9]',
            duration='0s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='testCountGenerateSecretFunction()',
            method_name='testCountGenerateSecretFunction()',
            duration='0.001s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='testCountPartialMatchesFunction()',
            method_name='testCountPartialMatchesFunction()',
            duration='0.071s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[10] ABBA, ABCD, 2, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)[10]',
            duration='0.001s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[11] AAAA, ABBB, 1, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)[11]',
            duration='0s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[12] BBBB, BBDH, 2, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)[12]',
            duration='0.002s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[13] AAAA, ABCD, 1, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)[13]',
            duration='0.006s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[1] ACEB, BCDF, 1, 1',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)[1]',
            duration='0.001s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[2] ABCD, ABCD, 4, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)[2]',
            duration='0.001s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[3] ABCD, DCBA, 0, 4',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)[3]',
            duration='0s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[4] ABCD, DBCA, 2, 2',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)[4]',
            duration='0s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[5] ABCD, EBCF, 2, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)[5]',
            duration='0.004s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[6] AAAA, AAAA, 4, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)[6]',
            duration='0.001s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[7] AAAA, BBBB, 0, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)[7]',
            duration='0s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[8] AABB, BBAA, 0, 4',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)[8]',
            duration='0s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[9] ABCD, ABBA, 2, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)[9]',
            duration='0s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='testGetGameRulesFunction()',
            method_name='testGetGameRulesFunction()',
            duration='0.001s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='testIsCompleteFunction()',
            method_name='testIsCompleteFunction()',
            duration='0s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[1] ACEB, BCDF, false',
            method_name='testIsCompleteImplementation(String, String, boolean)[1]',
            duration='0.003s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[2] ACEB, ACEB, true',
            method_name='testIsCompleteImplementation(String, String, boolean)[2]',
            duration='0s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='testSolution()',
            method_name='testSolution()',
            duration='0.016s',
            result='passed',
        ),
    ],
    2: None,
    3: [
        TestData(
            class_name='Test',
            test='testCountExactMatchesFunction()',
            method_name='testCountExactMatchesFunction()',
            duration='0s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[10] ABBA, ABCD, 2, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)[10]',
            duration='0.001s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[11] AAAA, ABBB, 1, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)[11]',
            duration='0.001s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[12] BBBB, BBDH, 2, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)[12]',
            duration='0s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[13] AAAA, ABCD, 1, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)[13]',
            duration='0s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[1] ACEB, BCDF, 1, 1',
            method_name='testCountExactMatchesImplementation(String, String, int, int)[1]',
            duration='0.012s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[2] ABCD, ABCD, 4, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)[2]',
            duration='0.001s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[3] ABCD, DCBA, 0, 4',
            method_name='testCountExactMatchesImplementation(String, String, int, int)[3]',
            duration='0.001s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[4] ABCD, DBCA, 2, 2',
            method_name='testCountExactMatchesImplementation(String, String, int, int)[4]',
            duration='0s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[5] ABCD, EBCF, 2, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)[5]',
            duration='0s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[6] AAAA, AAAA, 4, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)[6]',
            duration='0s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[7] AAAA, BBBB, 0, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)[7]',
            duration='0s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[8] AABB, BBAA, 0, 4',
            method_name='testCountExactMatchesImplementation(String, String, int, int)[8]',
            duration='0s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[9] ABCD, ABBA, 2, 0',
            method_name='testCountExactMatchesImplementation(String, String, int, int)[9]',
            duration='0s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='testCountGenerateSecretFunction()',
            method_name='testCountGenerateSecretFunction()',
            duration='0.001s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='testCountPartialMatchesFunction()',
            method_name='testCountPartialMatchesFunction()',
            duration='0.021s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[10] ABBA, ABCD, 2, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)[10]',
            duration='0.001s',
            result='failed',
            error_class='java.lang.StringIndexOutOfBoundsException',
            message='Index 4 out of bounds for length 4',
        ),
        TestData(
            class_name='Test',
            test='[11] AAAA, ABBB, 1, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)[11]',
            duration='0.001s',
            result='failed',
            error_class='java.lang.StringIndexOutOfBoundsException',
            message='Index 4 out of bounds for length 4',
        ),
        TestData(
            class_name='Test',
            test='[12] BBBB, BBDH, 2, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)[12]',
            duration='0.001s',
            result='failed',
            error_class='java.lang.StringIndexOutOfBoundsException',
            message='Index 4 out of bounds for length 4',
        ),
        TestData(
            class_name='Test',
            test='[13] AAAA, ABCD, 1, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)[13]',
            duration='0.001s',
            result='failed',
            error_class='java.lang.StringIndexOutOfBoundsException',
            message='Index 4 out of bounds for length 4',
        ),
        TestData(
            class_name='Test',
            test='[1] ACEB, BCDF, 1, 1',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)[1]',
            duration='0.003s',
            result='failed',
            error_class='java.lang.StringIndexOutOfBoundsException',
            message='Index 4 out of bounds for length 4',
        ),
        TestData(
            class_name='Test',
            test='[2] ABCD, ABCD, 4, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)[2]',
            duration='0s',
            result='failed',
            error_class='java.lang.StringIndexOutOfBoundsException',
            message='Index 4 out of bounds for length 4',
        ),
        TestData(
            class_name='Test',
            test='[3] ABCD, DCBA, 0, 4',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)[3]',
            duration='0.001s',
            result='failed',
            error_class='java.lang.StringIndexOutOfBoundsException',
            message='Index 4 out of bounds for length 4',
        ),
        TestData(
            class_name='Test',
            test='[4] ABCD, DBCA, 2, 2',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)[4]',
            duration='0.001s',
            result='failed',
            error_class='java.lang.StringIndexOutOfBoundsException',
            message='Index 4 out of bounds for length 4',
        ),
        TestData(
            class_name='Test',
            test='[5] ABCD, EBCF, 2, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)[5]',
            duration='0s',
            result='failed',
            error_class='java.lang.StringIndexOutOfBoundsException',
            message='Index 4 out of bounds for length 4',
        ),
        TestData(
            class_name='Test',
            test='[6] AAAA, AAAA, 4, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)[6]',
            duration='0s',
            result='failed',
            error_class='java.lang.StringIndexOutOfBoundsException',
            message='Index 4 out of bounds for length 4',
        ),
        TestData(
            class_name='Test',
            test='[7] AAAA, BBBB, 0, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)[7]',
            duration='0.001s',
            result='failed',
            error_class='java.lang.StringIndexOutOfBoundsException',
            message='Index 4 out of bounds for length 4',
        ),
        TestData(
            class_name='Test',
            test='[8] AABB, BBAA, 0, 4',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)[8]',
            duration='0.001s',
            result='failed',
            error_class='java.lang.StringIndexOutOfBoundsException',
            message='Index 4 out of bounds for length 4',
        ),
        TestData(
            class_name='Test',
            test='[9] ABCD, ABBA, 2, 0',
            method_name='testCountPartialMatchesImplementation(String, String, int, int)[9]',
            duration='0.001s',
            result='failed',
            error_class='java.lang.StringIndexOutOfBoundsException',
            message='Index 4 out of bounds for length 4',
        ),
        TestData(
            class_name='Test',
            test='testGetGameRulesFunction()',
            method_name='testGetGameRulesFunction()',
            duration='0s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='testIsCompleteFunction()',
            method_name='testIsCompleteFunction()',
            duration='0.001s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[1] ACEB, BCDF, false',
            method_name='testIsCompleteImplementation(String, String, boolean)[1]',
            duration='0.003s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='[2] ACEB, ACEB, true',
            method_name='testIsCompleteImplementation(String, String, boolean)[2]',
            duration='0s',
            result='passed',
        ),
        TestData(
            class_name='Test',
            test='testSolution()',
            method_name='testSolution()',
            duration='0.012s',
            result='passed',
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
        _parse_stderr_logs(TESTS_PARSER_FOLDER / 'gradle_logs' / str(submission_id), task_path)
        == SUBMISSIONS_ID_TO_EXPECTED_EXCEPTIONS[submission_id]
    )


@pytest.mark.parametrize('submission_id', range(4))
def test_parse_test_logs(submission_id: int):
    assert (
        _parse_test_logs(TESTS_PARSER_FOLDER / 'gradle_logs' / str(submission_id))
        == SUBMISSIONS_ID_TO_EXPECTED_TEST[submission_id]
    )


@pytest.mark.parametrize('submission_id', range(4))
def test_parse_gradle_logs(submission_id: int):
    submissions = pd.read_csv(TESTS_PARSER_FOLDER / 'submissions.csv')

    actual_parsed_logs = parse_gradle_logs(
        submissions[submissions[EduColumnName.ID.value] == submission_id].squeeze(), TESTS_PARSER_FOLDER / 'gradle_logs'
    )

    actual_exceptions, actual_tests = actual_parsed_logs
    actual_exceptions = (
        None
        if actual_exceptions is None
        else [ExceptionData(**exception_data) for exception_data in json.loads(actual_exceptions)]
    )
    actual_tests = None if actual_tests is None else [TestData(**test_data) for test_data in json.loads(actual_tests)]

    expected_exceptions = SUBMISSIONS_ID_TO_EXPECTED_EXCEPTIONS[submission_id]
    expected_tests = SUBMISSIONS_ID_TO_EXPECTED_TEST[submission_id]

    assert actual_exceptions == expected_exceptions
    assert actual_tests == expected_tests


def test_functional():
    with TemporaryDirectory() as tmp_dir:
        shutil.copyfile(TESTS_PARSER_FOLDER / 'submissions.csv', Path(tmp_dir) / 'submissions.csv')

        command = [
            sys.executable,
            (MAIN_FOLDER.parent / 'test_logs' / 'logs_parser.py'),
            (Path(tmp_dir) / 'submissions.csv'),
            (TESTS_PARSER_FOLDER / 'gradle_logs'),
        ]

        run_in_subprocess(command)

        expected_submissions = pd.read_csv(Path(tmp_dir) / 'submissions-with_parsed_logs.csv')
        actual_submissions = pd.read_csv(TESTS_PARSER_FOLDER / 'submissions-with_parsed_logs.csv')

        for expected_row, actual_row in zip(expected_submissions.itertuples(), actual_submissions.itertuples()):
            expected_tests = (
                None
                if pd.isna(getattr(expected_row, EduColumnName.TESTS.value))
                else [
                    TestData(**test_data) for test_data in json.loads(getattr(expected_row, EduColumnName.TESTS.value))
                ]
            )

            actual_tests = (
                None
                if pd.isna(getattr(actual_row, EduColumnName.TESTS.value))
                else [TestData(**test_data) for test_data in json.loads(getattr(actual_row, EduColumnName.TESTS.value))]
            )

            assert expected_tests == actual_tests

            expected_exceptions = (
                None
                if pd.isna(getattr(expected_row, EduColumnName.EXCEPTIONS.value))
                else [
                    ExceptionData(**exception_data)
                    for exception_data in json.loads(getattr(expected_row, EduColumnName.EXCEPTIONS.value))
                ]
            )

            actual_exceptions = (
                None
                if pd.isna(getattr(actual_row, EduColumnName.EXCEPTIONS.value))
                else [
                    ExceptionData(**exception_data)
                    for exception_data in json.loads(getattr(actual_row, EduColumnName.EXCEPTIONS.value))
                ]
            )

            assert expected_exceptions == actual_exceptions

        expected_submissions_without_parsed_logs = expected_submissions.drop(
            columns=[EduColumnName.EXCEPTIONS.value, EduColumnName.TESTS.value],
        )

        actual_submissions_without_parsed_logs = actual_submissions.drop(
            columns=[EduColumnName.EXCEPTIONS.value, EduColumnName.TESTS.value],
        )

        # Asserting that other columns didn't change
        assert_frame_equal(expected_submissions_without_parsed_logs, actual_submissions_without_parsed_logs)


def test_functional_incorrect_arguments():
    command = [sys.executable, (MAIN_FOLDER.parent / 'test_logs' / 'logs_parser.py')]

    stdout, stderr = run_in_subprocess(command)

    assert stdout == ''
    assert 'error: the following arguments are required' in stderr
