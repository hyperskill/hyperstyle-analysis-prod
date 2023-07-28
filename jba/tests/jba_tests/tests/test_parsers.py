import pytest
from typing import List

from pathlib import Path

from jba.models.edu_logs import ExceptionData, TestData
from jba.tests.parsers import parse_gradle_stderr_logs, parse_gradle_test_logs
from jba_tests.tests import TESTS_FOLDER

PARSERS_FOLDER = TESTS_FOLDER / 'parsers'


PARSE_GRADLE_STDERR_LOGS_DATA = [
    (PARSERS_FOLDER / 'stderr_logs_without_exceptions.txt', []),
    (
        PARSERS_FOLDER / 'stderr_logs_with_exceptions.txt',
        [
            ExceptionData(
                path='src/main/kotlin/Main.kt',
                line_number=2,
                column_number=49,
                message="Expecting '\"'",
            ),
            ExceptionData(
                path='src/main/kotlin/Main.kt',
                line_number=3,
                column_number=30,
                message='Expecting an element',
            ),
            ExceptionData(
                path='src/main/kotlin/Main.kt',
                line_number=3,
                column_number=50,
                message="Expecting ','",
            ),
            ExceptionData(
                path='src/main/kotlin/Main.kt',
                line_number=4,
                column_number=25,
                message='Expecting an element',
            ),
            ExceptionData(
                path='src/main/kotlin/Main.kt',
                line_number=4,
                column_number=42,
                message='Expecting an element',
            ),
        ],
    ),
]


@pytest.mark.parametrize(('stderr_logs_path', 'expected_exceptions'), PARSE_GRADLE_STDERR_LOGS_DATA)
def test_parse_gradle_stderr_logs(stderr_logs_path: Path, expected_exceptions: List[ExceptionData]):
    assert expected_exceptions == parse_gradle_stderr_logs(stderr_logs_path, 'Introduction/LastPush/FinishTheApp')


PARSE_GRADLE_TEST_LOGS_DATA = [
    (
        PARSERS_FOLDER / 'test_logs_all_passed.html',
        [
            TestData(
                class_name='Test',
                test='testCountExactMatchesFunction()',
                method_name='testCountExactMatchesFunction()',
                duration='0.001s',
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
                duration='0.031s',
                result='passed',
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
                test='testPlayGameFunction()',
                method_name='testPlayGameFunction()',
                duration='0s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test='testSolution()',
                method_name='testSolution()',
                duration='0.014s',
                result='passed',
            ),
        ],
    ),
    (
        PARSERS_FOLDER / 'test_logs_several_failed.html',
        [
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
                duration='0s',
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
                duration='0.003s',
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
                duration='0s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test='testCountPartialMatchesFunction()',
                method_name='testCountPartialMatchesFunction()',
                duration='0.028s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test='[10] ABBA, ABCD, 2, 0',
                method_name='testCountPartialMatchesImplementation(String, String, int, int)[10]',
                duration='0s',
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
                duration='0.001s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test='[13] AAAA, ABCD, 1, 0',
                method_name='testCountPartialMatchesImplementation(String, String, int, int)[13]',
                duration='0s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test='[1] ACEB, BCDF, 1, 1',
                method_name='testCountPartialMatchesImplementation(String, String, int, int)[1]',
                duration='0s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test='[2] ABCD, ABCD, 4, 0',
                method_name='testCountPartialMatchesImplementation(String, String, int, int)[2]',
                duration='0s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test='[3] ABCD, DCBA, 0, 4',
                method_name='testCountPartialMatchesImplementation(String, String, int, int)[3]',
                duration='0.001s',
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
                duration='0s',
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
                duration='0.001s',
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
                duration='0.002s',
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
                test='testIsLostFunction()',
                method_name='testIsLostFunction()',
                duration='0s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test='[1] true, 3, 4, true, false',
                method_name='testIsLostImplementation(boolean, int, int, boolean, boolean)[1]',
                duration='0.006s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test='[2] true, 4, 4, true, false',
                method_name='testIsLostImplementation(boolean, int, int, boolean, boolean)[2]',
                duration='0.001s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test='[3] false, 4, 4, false, false',
                method_name='testIsLostImplementation(boolean, int, int, boolean, boolean)[3]',
                duration='0.001s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test='[4] false, 5, 4, false, true',
                method_name='testIsLostImplementation(boolean, int, int, boolean, boolean)[4]',
                duration='0s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test='[5] false, 3, 4, false, false',
                method_name='testIsLostImplementation(boolean, int, int, boolean, boolean)[5]',
                duration='0s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test='testIsWinFunction()',
                method_name='testIsWinFunction()',
                duration='0s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test='[1] true, 3, 4, true, false',
                method_name='testIsWinImplementation(boolean, int, int, boolean, boolean)[1]',
                duration='0.002s',
                result='failed',
                error_class='org.opentest4j.AssertionFailedError',
                message=(
                    'The function isWin must return true for the following arguments: complete: true, attempts: 3, '
                    'maxAttemptsCount: 4 ==> expected: <true> but was: <false>'
                ),
            ),
            TestData(
                class_name='Test',
                test='[2] true, 4, 4, true, false',
                method_name='testIsWinImplementation(boolean, int, int, boolean, boolean)[2]',
                duration='0.001s',
                result='failed',
                error_class='org.opentest4j.AssertionFailedError',
                message=(
                    'The function isWin must return true for the following arguments: complete: true, attempts: 4, '
                    'maxAttemptsCount: 4 ==> expected: <true> but was: <false>'
                ),
            ),
            TestData(
                class_name='Test',
                test='[3] false, 4, 4, false, false',
                method_name='testIsWinImplementation(boolean, int, int, boolean, boolean)[3]',
                duration='0.001s',
                result='failed',
                error_class='org.opentest4j.AssertionFailedError',
                message=(
                    'The function isWin must return false for the following arguments: complete: false, attempts: 4, '
                    'maxAttemptsCount: 4 ==> expected: <false> but was: <true>'
                ),
            ),
            TestData(
                class_name='Test',
                test='[4] false, 5, 4, false, true',
                method_name='testIsWinImplementation(boolean, int, int, boolean, boolean)[4]',
                duration='0.001s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test='[5] false, 3, 4, false, false',
                method_name='testIsWinImplementation(boolean, int, int, boolean, boolean)[5]',
                duration='0.001s',
                result='failed',
                error_class='org.opentest4j.AssertionFailedError',
                message=(
                    'The function isWin must return false for the following arguments: complete: false, attempts: 3, '
                    'maxAttemptsCount: 4 ==> expected: <false> but was: <true>'
                ),
            ),
            TestData(
                class_name='Test',
                test='testPrintRoundResultsFunction()',
                method_name='testPrintRoundResultsFunction()',
                duration='0s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test=(
                    '[1] ABCD, [GameStep(attempt=BCDF, positions=0, letters=3), '
                    'GameStep(attempt=ABCD, positions=4, letters=0)], WIN'
                ),
                method_name='testSolution(String, List, GameResult)[1]',
                duration='0.021s',
                result='failed',
                error_class='java.lang.AssertionError',
                message='You are asking the user to enter data fewer times than required in the task!',
            ),
            TestData(
                class_name='Test',
                test=(
                    '[2] ABCD, [GameStep(attempt=BCDF, positions=0, letters=3), GameStep(attempt=ABDC, '
                    'positions=2, letters=2), GameStep(attempt=ABCD, positions=4, letters=0)], WIN'
                ),
                method_name='testSolution(String, List, GameResult)[2]',
                duration='0.001s',
                result='failed',
                error_class='java.lang.AssertionError',
                message='You are asking the user to enter data fewer times than required in the task!',
            ),
            TestData(
                class_name='Test',
                test=(
                    '[3] ABCD, [GameStep(attempt=BCDF, positions=0, letters=3), '
                    'GameStep(attempt=BCDF, positions=0, letters=3), GameStep(attempt=BCDF, '
                    'positions=0, letters=3), GameStep(attempt=BCDF, positions=0, letters=3)], LOSE'
                ),
                method_name='testSolution(String, List, GameResult)[3]',
                duration='0.004s',
                result='failed',
                error_class='java.lang.AssertionError',
                message='You are asking the user to enter data fewer times than required in the task!',
            ),
        ],
    ),
    (
        PARSERS_FOLDER / 'test_logs_gradle.html',
        [
            TestData(
                class_name='Gradle Test Executor 357',
                test='failed to execute tests',
                method_name='failed to execute tests',
                duration='0.902s',
                result='failed',
                error_class='org.gradle.api.internal.tasks.testing.TestSuiteExecutionException',
                message='Could not complete execution for Gradle Test Executor 357.',
            ),
        ],
    ),
]


@pytest.mark.parametrize(('test_logs_path', 'expected_tests'), PARSE_GRADLE_TEST_LOGS_DATA)
def test_parse_gradle_test_logs(test_logs_path: Path, expected_tests: List[TestData]):
    assert expected_tests == parse_gradle_test_logs(test_logs_path)
