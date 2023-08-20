from textwrap import dedent

import pytest
from typing import List

from pathlib import Path

from jba.src.models.edu_logs import ExceptionData, TestData
from jba.src.test_logs.parsers import parse_gradle_stderr_logs, parse_gradle_test_logs
from jba.tests.test_logs import TEST_LOGS_FOLDER

PARSERS_FOLDER = TEST_LOGS_FOLDER / 'parsers'


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
                test='ABBA, ABCD, 2, 0',
                method_name='testCountExactMatchesImplementation(String, String, int, int)',
                duration='0s',
                result='passed',
                test_number=10,
            ),
            TestData(
                class_name='Test',
                test='AAAA, ABBB, 1, 0',
                method_name='testCountExactMatchesImplementation(String, String, int, int)',
                duration='0.001s',
                result='passed',
                test_number=11,
            ),
            TestData(
                class_name='Test',
                test='BBBB, BBDH, 2, 0',
                method_name='testCountExactMatchesImplementation(String, String, int, int)',
                duration='0.001s',
                result='passed',
                test_number=12,
            ),
            TestData(
                class_name='Test',
                test='AAAA, ABCD, 1, 0',
                method_name='testCountExactMatchesImplementation(String, String, int, int)',
                duration='0s',
                result='passed',
                test_number=13,
            ),
            TestData(
                class_name='Test',
                test='ACEB, BCDF, 1, 1',
                method_name='testCountExactMatchesImplementation(String, String, int, int)',
                duration='0.003s',
                result='passed',
                test_number=1,
            ),
            TestData(
                class_name='Test',
                test='ABCD, ABCD, 4, 0',
                method_name='testCountExactMatchesImplementation(String, String, int, int)',
                duration='0.001s',
                result='passed',
                test_number=2,
            ),
            TestData(
                class_name='Test',
                test='ABCD, DCBA, 0, 4',
                method_name='testCountExactMatchesImplementation(String, String, int, int)',
                duration='0.001s',
                result='passed',
                test_number=3,
            ),
            TestData(
                class_name='Test',
                test='ABCD, DBCA, 2, 2',
                method_name='testCountExactMatchesImplementation(String, String, int, int)',
                duration='0.001s',
                result='passed',
                test_number=4,
            ),
            TestData(
                class_name='Test',
                test='ABCD, EBCF, 2, 0',
                method_name='testCountExactMatchesImplementation(String, String, int, int)',
                duration='0.001s',
                result='passed',
                test_number=5,
            ),
            TestData(
                class_name='Test',
                test='AAAA, AAAA, 4, 0',
                method_name='testCountExactMatchesImplementation(String, String, int, int)',
                duration='0s',
                result='passed',
                test_number=6,
            ),
            TestData(
                class_name='Test',
                test='AAAA, BBBB, 0, 0',
                method_name='testCountExactMatchesImplementation(String, String, int, int)',
                duration='0s',
                result='passed',
                test_number=7,
            ),
            TestData(
                class_name='Test',
                test='AABB, BBAA, 0, 4',
                method_name='testCountExactMatchesImplementation(String, String, int, int)',
                duration='0s',
                result='passed',
                test_number=8,
            ),
            TestData(
                class_name='Test',
                test='ABCD, ABBA, 2, 0',
                method_name='testCountExactMatchesImplementation(String, String, int, int)',
                duration='0s',
                result='passed',
                test_number=9,
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
                test='ABBA, ABCD, 2, 0',
                method_name='testCountPartialMatchesImplementation(String, String, int, int)',
                duration='0s',
                result='passed',
                test_number=10,
            ),
            TestData(
                class_name='Test',
                test='AAAA, ABBB, 1, 0',
                method_name='testCountPartialMatchesImplementation(String, String, int, int)',
                duration='0s',
                result='passed',
                test_number=11,
            ),
            TestData(
                class_name='Test',
                test='BBBB, BBDH, 2, 0',
                method_name='testCountPartialMatchesImplementation(String, String, int, int)',
                duration='0.001s',
                result='passed',
                test_number=12,
            ),
            TestData(
                class_name='Test',
                test='AAAA, ABCD, 1, 0',
                method_name='testCountPartialMatchesImplementation(String, String, int, int)',
                duration='0s',
                result='passed',
                test_number=13,
            ),
            TestData(
                class_name='Test',
                test='ACEB, BCDF, 1, 1',
                method_name='testCountPartialMatchesImplementation(String, String, int, int)',
                duration='0s',
                result='passed',
                test_number=1,
            ),
            TestData(
                class_name='Test',
                test='ABCD, ABCD, 4, 0',
                method_name='testCountPartialMatchesImplementation(String, String, int, int)',
                duration='0s',
                result='passed',
                test_number=2,
            ),
            TestData(
                class_name='Test',
                test='ABCD, DCBA, 0, 4',
                method_name='testCountPartialMatchesImplementation(String, String, int, int)',
                duration='0.001s',
                result='passed',
                test_number=3,
            ),
            TestData(
                class_name='Test',
                test='ABCD, DBCA, 2, 2',
                method_name='testCountPartialMatchesImplementation(String, String, int, int)',
                duration='0s',
                result='passed',
                test_number=4,
            ),
            TestData(
                class_name='Test',
                test='ABCD, EBCF, 2, 0',
                method_name='testCountPartialMatchesImplementation(String, String, int, int)',
                duration='0s',
                result='passed',
                test_number=5,
            ),
            TestData(
                class_name='Test',
                test='AAAA, AAAA, 4, 0',
                method_name='testCountPartialMatchesImplementation(String, String, int, int)',
                duration='0.001s',
                result='passed',
                test_number=6,
            ),
            TestData(
                class_name='Test',
                test='AAAA, BBBB, 0, 0',
                method_name='testCountPartialMatchesImplementation(String, String, int, int)',
                duration='0s',
                result='passed',
                test_number=7,
            ),
            TestData(
                class_name='Test',
                test='AABB, BBAA, 0, 4',
                method_name='testCountPartialMatchesImplementation(String, String, int, int)',
                duration='0s',
                result='passed',
                test_number=8,
            ),
            TestData(
                class_name='Test',
                test='ABCD, ABBA, 2, 0',
                method_name='testCountPartialMatchesImplementation(String, String, int, int)',
                duration='0.001s',
                result='passed',
                test_number=9,
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
                test='ACEB, BCDF, false',
                method_name='testIsCompleteImplementation(String, String, boolean)',
                duration='0.002s',
                result='passed',
                test_number=1,
            ),
            TestData(
                class_name='Test',
                test='ACEB, ACEB, true',
                method_name='testIsCompleteImplementation(String, String, boolean)',
                duration='0s',
                result='passed',
                test_number=2,
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
                test='true, 3, 4, true, false',
                method_name='testIsLostImplementation(boolean, int, int, boolean, boolean)',
                duration='0.006s',
                result='passed',
                test_number=1,
            ),
            TestData(
                class_name='Test',
                test='true, 4, 4, true, false',
                method_name='testIsLostImplementation(boolean, int, int, boolean, boolean)',
                duration='0.001s',
                result='passed',
                test_number=2,
            ),
            TestData(
                class_name='Test',
                test='false, 4, 4, false, false',
                method_name='testIsLostImplementation(boolean, int, int, boolean, boolean)',
                duration='0.001s',
                result='passed',
                test_number=3,
            ),
            TestData(
                class_name='Test',
                test='false, 5, 4, false, true',
                method_name='testIsLostImplementation(boolean, int, int, boolean, boolean)',
                duration='0s',
                result='passed',
                test_number=4,
            ),
            TestData(
                class_name='Test',
                test='false, 3, 4, false, false',
                method_name='testIsLostImplementation(boolean, int, int, boolean, boolean)',
                duration='0s',
                result='passed',
                test_number=5,
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
                test='true, 3, 4, true, false',
                method_name='testIsWinImplementation(boolean, int, int, boolean, boolean)',
                duration='0.002s',
                result='failed',
                test_number=1,
                error_class='org.opentest4j.AssertionFailedError',
                message=(
                    'The function isWin must return true for the following arguments: complete: true, attempts: 3, '
                    'maxAttemptsCount: 4 ==> expected: <true> but was: <false>'
                ),
            ),
            TestData(
                class_name='Test',
                test='true, 4, 4, true, false',
                method_name='testIsWinImplementation(boolean, int, int, boolean, boolean)',
                duration='0.001s',
                result='failed',
                test_number=2,
                error_class='org.opentest4j.AssertionFailedError',
                message=(
                    'The function isWin must return true for the following arguments: complete: true, attempts: 4, '
                    'maxAttemptsCount: 4 ==> expected: <true> but was: <false>'
                ),
            ),
            TestData(
                class_name='Test',
                test='false, 4, 4, false, false',
                method_name='testIsWinImplementation(boolean, int, int, boolean, boolean)',
                duration='0.001s',
                result='failed',
                test_number=3,
                error_class='org.opentest4j.AssertionFailedError',
                message=(
                    'The function isWin must return false for the following arguments: complete: false, attempts: 4, '
                    'maxAttemptsCount: 4 ==> expected: <false> but was: <true>'
                ),
            ),
            TestData(
                class_name='Test',
                test='false, 5, 4, false, true',
                method_name='testIsWinImplementation(boolean, int, int, boolean, boolean)',
                duration='0.001s',
                result='passed',
                test_number=4,
            ),
            TestData(
                class_name='Test',
                test='false, 3, 4, false, false',
                method_name='testIsWinImplementation(boolean, int, int, boolean, boolean)',
                duration='0.001s',
                result='failed',
                test_number=5,
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
                    'ABCD, [GameStep(attempt=BCDF, positions=0, letters=3), '
                    'GameStep(attempt=ABCD, positions=4, letters=0)], WIN'
                ),
                method_name='testSolution(String, List, GameResult)',
                duration='0.021s',
                result='failed',
                test_number=1,
                error_class='java.lang.AssertionError',
                message='You are asking the user to enter data fewer times than required in the task!',
            ),
            TestData(
                class_name='Test',
                test=(
                    'ABCD, [GameStep(attempt=BCDF, positions=0, letters=3), GameStep(attempt=ABDC, '
                    'positions=2, letters=2), GameStep(attempt=ABCD, positions=4, letters=0)], WIN'
                ),
                method_name='testSolution(String, List, GameResult)',
                duration='0.001s',
                result='failed',
                test_number=2,
                error_class='java.lang.AssertionError',
                message='You are asking the user to enter data fewer times than required in the task!',
            ),
            TestData(
                class_name='Test',
                test=(
                    'ABCD, [GameStep(attempt=BCDF, positions=0, letters=3), '
                    'GameStep(attempt=BCDF, positions=0, letters=3), GameStep(attempt=BCDF, '
                    'positions=0, letters=3), GameStep(attempt=BCDF, positions=0, letters=3)], LOSE'
                ),
                method_name='testSolution(String, List, GameResult)',
                duration='0.004s',
                result='failed',
                test_number=3,
                error_class='java.lang.AssertionError',
                message='You are asking the user to enter data fewer times than required in the task!',
            ),
        ],
    ),
    (
        PARSERS_FOLDER / 'test_logs_several_failed_with_multiline_test_cases.html',
        [
            TestData(
                class_name='Test',
                test='canvasGeneratorFunction()',
                method_name='canvasGeneratorFunction()',
                duration='0s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                     X
                    / \
                    \ /
                     X, Filter(width=6, height=8, result= X  X  X  X  X  X 
                    / \/ \/ \/ \/ \/ \
                    \ /\ /\ /\ /\ /\ /
                     X  X  X  X  X  X 
                    / \/ \/ \/ \/ \/ \
                    \ /\ /\ /\ /\ /\ /
                     X  X  X  X  X  X 
                    / \/ \/ \/ \/ \/ \
                    \ /\ /\ /\ /\ /\ /
                     X  X  X  X  X  X 
                    / \/ \/ \/ \/ \/ \
                    \ /\ /\ /\ /\ /\ /
                     X  X  X  X  X  X 
                    / \/ \/ \/ \/ \/ \
                    \ /\ /\ /\ /\ /\ /
                     X  X  X  X  X  X 
                    / \/ \/ \/ \/ \/ \
                    \ /\ /\ /\ /\ /\ /
                     X  X  X  X  X  X 
                    / \/ \/ \/ \/ \/ \
                    \ /\ /\ /\ /\ /\ /
                     X  X  X  X  X  X 
                    / \/ \/ \/ \/ \/ \
                    \ /\ /\ /\ /\ /\ /
                     X  X  X  X  X  X )
                    """
                ).strip('\n'),
                method_name='canvasGeneratorImplementation(String, Filter)',
                duration='0.001s',
                result='passed',
                test_number=10,
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                      ____   
                     /    \
                    / /  \ \
                    \ \__/ /
                     \____/, Filter(width=1, height=1, result=  ____   
                     /    \  
                    / /  \ \ 
                    \ \__/ / 
                     \____/  )
                    """
                ).strip('\n'),
                method_name='canvasGeneratorImplementation(String, Filter)',
                duration='0.001s',
                result='passed',
                test_number=11,
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                      ____   
                     /    \
                    / /  \ \
                    \ \__/ /
                     \____/, Filter(width=2, height=1, result=  ____     ____   
                     /    \   /    \  
                    / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / 
                     \____/   \____/  )
                    """
                ).strip('\n'),
                method_name='canvasGeneratorImplementation(String, Filter)',
                duration='0.001s',
                result='passed',
                test_number=12,
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                      ____   
                     /    \
                    / /  \ \
                    \ \__/ /
                     \____/, Filter(width=1, height=2, result=  ____   
                     /    \  
                    / /  \ \ 
                    \ \__/ / 
                     \____/  
                     /    \  
                    / /  \ \ 
                    \ \__/ / 
                     \____/  )
                    """
                ).strip('\n'),
                method_name='canvasGeneratorImplementation(String, Filter)',
                duration='0.004s',
                result='failed',
                test_number=13,
                error_class='org.opentest4j.AssertionFailedError',
                message=dedent(
                    r"""
                    For pattern:
                      ____   
                     /    \
                    / /  \ \
                    \ \__/ /
                     \____/
                    , width=1, and height=2 the function canvasGenerator should return 
                      ____   
                     /    \  
                    / /  \ \ 
                    \ \__/ / 
                     \____/  
                     /    \  
                    / /  \ \ 
                    \ \__/ / 
                     \____/  
                     ==> expected: <  ____   
                     /    \  
                    / /  \ \ 
                    \ \__/ / 
                     \____/  
                     /    \  
                    / /  \ \ 
                    \ \__/ / 
                     \____/  > but was: <  ____   
                     /    \  
                    / /  \ \ 
                    \ \__/ / 
                     \____/  
                     /    \ 
                    / /  \ \
                    \ \__/ /
                     \____/ >
                    """
                ).strip('\n'),
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                      ____   
                     /    \
                    / /  \ \
                    \ \__/ /
                     \____/, Filter(width=5, height=7, result=  ____     ____     ____     ____     ____   
                     /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ …
                    """
                ).strip('\n'),
                method_name='canvasGeneratorImplementation(String, Filter)',
                duration='0.002s',
                result='failed',
                test_number=14,
                error_class='org.opentest4j.AssertionFailedError',
                message=dedent(
                    r"""
                    For pattern:
                      ____   
                     /    \
                    / /  \ \
                    \ \__/ /
                     \____/
                    , width=5, and height=7 the function canvasGenerator should return 
                      ____     ____     ____     ____     ____   
                     /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/  
                     ==> expected: <  ____     ____     ____     ____     ____   
                     /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/  > but was: <  ____     ____     ____     ____     ____   
                     /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/  
                     /    \  /    \  /    \  /    \  /    \ 
                    / /  \ \/ /  \ \/ /  \ \/ /  \ \/ /  \ \
                    \ \__/ /\ \__/ /\ \__/ /\ \__/ /\ \__/ /
                     \____/  \____/  \____/  \____/  \____/ 
                     /    \  /    \  /    \  /    \  /    \ 
                    / /  \ \/ /  \ \/ /  \ \/ /  \ \/ /  \ \
                    \ \__/ /\ \__/ /\ \__/ /\ \__/ /\ \__/ /
                     \____/  \____/  \____/  \____/  \____/ 
                     /    \  /    \  /    \  /    \  /    \ 
                    / /  \ \/ /  \ \/ /  \ \/ /  \ \/ /  \ \
                    \ \__/ /\ \__/ /\ \__/ /\ \__/ /\ \__/ /
                     \____/  \____/  \____/  \____/  \____/ 
                     /    \  /    \  /    \  /    \  /    \ 
                    / /  \ \/ /  \ \/ /  \ \/ /  \ \/ /  \ \
                    \ \__/ /\ \__/ /\ \__/ /\ \__/ /\ \__/ /
                     \____/  \____/  \____/  \____/  \____/ 
                     /    \  /    \  /    \  /    \  /    \ 
                    / /  \ \/ /  \ \/ /  \ \/ /  \ \/ /  \ \
                    \ \__/ /\ \__/ /\ \__/ /\ \__/ /\ \__/ /
                     \____/  \____/  \____/  \____/  \____/ 
                     /    \  /    \  /    \  /    \  /    \ 
                    / /  \ \/ /  \ \/ /  \ \/ /  \ \/ /  \ \
                    \ \__/ /\ \__/ /\ \__/ /\ \__/ /\ \__/ /
                     \____/  \____/  \____/  \____/  \____/ >
                    """
                ).strip('\n'),
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                      ____   
                     /    \
                    / /  \ \
                    \ \__/ /
                     \____/, Filter(width=6, height=8, result=  ____     ____     ____     ____     ____     ____   
                     /    \   /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \…
                    """
                ).strip('\n'),
                method_name='canvasGeneratorImplementation(String, Filter)',
                duration='0.002s',
                result='failed',
                test_number=15,
                error_class='org.opentest4j.AssertionFailedError',
                message=dedent(
                    r"""
                    For pattern:
                      ____   
                     /    \
                    / /  \ \
                    \ \__/ /
                     \____/
                    , width=6, and height=8 the function canvasGenerator should return 
                      ____     ____     ____     ____     ____     ____   
                     /    \   /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/   \____/  
                     ==> expected: <  ____     ____     ____     ____     ____     ____   
                     /    \   /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/   \____/  
                     /    \   /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/   \____/  > but was: <  ____     ____     ____     ____     ____     ____   
                     /    \   /    \   /    \   /    \   /    \   /    \  
                    / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / \ \__/ / 
                     \____/   \____/   \____/   \____/   \____/   \____/  
                     /    \  /    \  /    \  /    \  /    \  /    \ 
                    / /  \ \/ /  \ \/ /  \ \/ /  \ \/ /  \ \/ /  \ \
                    \ \__/ /\ \__/ /\ \__/ /\ \__/ /\ \__/ /\ \__/ /
                     \____/  \____/  \____/  \____/  \____/  \____/ 
                     /    \  /    \  /    \  /    \  /    \  /    \ 
                    / /  \ \/ /  \ \/ /  \ \/ /  \ \/ /  \ \/ /  \ \
                    \ \__/ /\ \__/ /\ \__/ /\ \__/ /\ \__/ /\ \__/ /
                     \____/  \____/  \____/  \____/  \____/  \____/ 
                     /    \  /    \  /    \  /    \  /    \  /    \ 
                    / /  \ \/ /  \ \/ /  \ \/ /  \ \/ /  \ \/ /  \ \
                    \ \__/ /\ \__/ /\ \__/ /\ \__/ /\ \__/ /\ \__/ /
                     \____/  \____/  \____/  \____/  \____/  \____/ 
                     /    \  /    \  /    \  /    \  /    \  /    \ 
                    / /  \ \/ /  \ \/ /  \ \/ /  \ \/ /  \ \/ /  \ \
                    \ \__/ /\ \__/ /\ \__/ /\ \__/ /\ \__/ /\ \__/ /
                     \____/  \____/  \____/  \____/  \____/  \____/ 
                     /    \  /    \  /    \  /    \  /    \  /    \ 
                    / /  \ \/ /  \ \/ /  \ \/ /  \ \/ /  \ \/ /  \ \
                    \ \__/ /\ \__/ /\ \__/ /\ \__/ /\ \__/ /\ \__/ /
                     \____/  \____/  \____/  \____/  \____/  \____/ 
                     /    \  /    \  /    \  /    \  /    \  /    \ 
                    / /  \ \/ /  \ \/ /  \ \/ /  \ \/ /  \ \/ /  \ \
                    \ \__/ /\ \__/ /\ \__/ /\ \__/ /\ \__/ /\ \__/ /
                     \____/  \____/  \____/  \____/  \____/  \____/ 
                     /    \  /    \  /    \  /    \  /    \  /    \ 
                    / /  \ \/ /  \ \/ /  \ \/ /  \ \/ /  \ \/ /  \ \
                    \ \__/ /\ \__/ /\ \__/ /\ \__/ /\ \__/ /\ \__/ /
                     \____/  \____/  \____/  \____/  \____/  \____/ >
                    """
                ).strip('\n'),
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    """
                    +---+---+
                    | o   o |
                    |   ^   |
                    |  ---  |
                    +---+---+, Filter(width=1, height=1, result=+---+---+
                    | o   o |
                    |   ^   |
                    |  ---  |
                    +---+---+)
                    """
                ).strip('\n'),
                method_name='canvasGeneratorImplementation(String, Filter)',
                duration='0s',
                result='passed',
                test_number=16,
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    """
                    +---+---+
                    | o   o |
                    |   ^   |
                    |  ---  |
                    +---+---+, Filter(width=2, height=1, result=+---+---++---+---+
                    | o   o || o   o |
                    |   ^   ||   ^   |
                    |  ---  ||  ---  |
                    +---+---++---+---+)
                    """
                ).strip('\n'),
                method_name='canvasGeneratorImplementation(String, Filter)',
                duration='0s',
                result='passed',
                test_number=17,
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    """
                    +---+---+
                    | o   o |
                    |   ^   |
                    |  ---  |
                    +---+---+, Filter(width=1, height=2, result=+---+---+
                    | o   o |
                    |   ^   |
                    |  ---  |
                    +---+---+
                    | o   o |
                    |   ^   |
                    |  ---  |
                    +---+---+)
                    """
                ).strip('\n'),
                method_name='canvasGeneratorImplementation(String, Filter)',
                duration='0.001s',
                result='passed',
                test_number=18,
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    """
                    +---+---+
                    | o   o |
                    |   ^   |
                    |  ---  |
                    +---+---+, Filter(width=5, height=7, result=+---+---++---+---++---+---++---+---++---+---+
                    | o   o || o   o || o   o || o   o || o   o |
                    |   ^   ||   ^   ||   ^   ||   ^   ||   ^   |
                    |  ---  ||  ---  ||  ---  ||  ---  ||  ---  |
                    +---+---++---+---++---+---++---+---++---+---+
                    | o   o || o   o || o   o || o   o || o   o |
                    |   ^   ||   ^   ||   ^   ||   ^   ||   ^   |
                    |  ---  ||  ---  ||  ---  ||  ---  ||  ---  |
                    +---+---++---+---++---+---++---+---++---+---+
                    | o   o || o   o || o   o || o   o || o   o |
                    |   ^   ||   ^   |…
                    """
                ).strip('\n'),
                method_name='canvasGeneratorImplementation(String, Filter)',
                duration='0.001s',
                result='passed',
                test_number=19,
            ),
            TestData(
                class_name='Test',
                test='○, Filter(width=1, height=1, result=○)',
                method_name='canvasGeneratorImplementation(String, Filter)',
                duration='0.004s',
                result='passed',
                test_number=1,
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    """
                    +---+---+
                    | o   o |
                    |   ^   |
                    |  ---  |
                    +---+---+, Filter(width=6, height=8, result=+---+---++---+---++---+---++---+---++---+---++---+---+
                    | o   o || o   o || o   o || o   o || o   o || o   o |
                    |   ^   ||   ^   ||   ^   ||   ^   ||   ^   ||   ^   |
                    |  ---  ||  ---  ||  ---  ||  ---  ||  ---  ||  ---  |
                    +---+---++---+---++---+---++---+---++---+---++---+---+
                    | o   o || o   o || o   o || o   o || o   o || o   o |
                    |   ^   ||   ^   ||   ^   ||   ^   ||   ^   ||   ^   |
                    |  ---  ||  ---  ||  ---  ||  ---  ||  ---  ||  ---  |
                    +---+---++---+---++---+---++---+---++-…
                    """
                ).strip('\n'),
                method_name='canvasGeneratorImplementation(String, Filter)',
                duration='0.001s',
                result='passed',
                test_number=20,
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    """
                       .+------+
                     .' |    .'|
                    +---+--+'  |
                    |   |  |   |
                    |  ,+--+---+
                    |.'    | .' 
                    +------+', Filter(width=1, height=1, result=   .+------+
                     .' |    .'|
                    +---+--+'  |
                    |   |  |   |
                    |  ,+--+---+
                    |.'    | .' 
                    +------+'   )
                    """
                ).strip('\n'),
                method_name='canvasGeneratorImplementation(String, Filter)',
                duration='0.001s',
                result='passed',
                test_number=21,
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    """
                       .+------+
                     .' |    .'|
                    +---+--+'  |
                    |   |  |   |
                    |  ,+--+---+
                    |.'    | .' 
                    +------+', Filter(width=2, height=1, result=   .+------+   .+------+
                     .' |    .'| .' |    .'|
                    +---+--+'  |+---+--+'  |
                    |   |  |   ||   |  |   |
                    |  ,+--+---+|  ,+--+---+
                    |.'    | .' |.'    | .' 
                    +------+'   +------+'   )
                    """
                ).strip('\n'),
                method_name='canvasGeneratorImplementation(String, Filter)',
                duration='0.001s',
                result='passed',
                test_number=22,
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    """
                       .+------+
                     .' |    .'|
                    +---+--+'  |
                    |   |  |   |
                    |  ,+--+---+
                    |.'    | .' 
                    +------+', Filter(width=1, height=2, result=   .+------+
                     .' |    .'|
                    +---+--+'  |
                    |   |  |   |
                    |  ,+--+---+
                    |.'    | .' 
                    +------+'   
                     .' |    .'|
                    +---+--+'  |
                    |   |  |   |
                    |  ,+--+---+
                    |.'    | .' 
                    +------+'   )
                    """
                ).strip('\n'),
                method_name='canvasGeneratorImplementation(String, Filter)',
                duration='0s',
                result='passed',
                test_number=23,
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    """
                       .+------+
                     .' |    .'|
                    +---+--+'  |
                    |   |  |   |
                    |  ,+--+---+
                    |.'    | .' 
                    +------+', Filter(width=5, height=7, result=   .+------+   .+------+   .+------+   .+------+   .+------+
                     .' |    .'| .' |    .'| .' |    .'| .' |    .'| .' |    .'|
                    +---+--+'  |+---+--+'  |+---+--+'  |+---+--+'  |+---+--+'  |
                    |   |  |   ||   |  |   ||   |  |   ||   |  |   ||   |  |   |
                    |  ,+--+---+|  ,+--+---+|  ,+--+---+|  ,+--+---+|  ,+--+---+
                    |.'    | .' |.'    | .' |.'    | .' |.'    | .' |.'    | .' 
                    +------+'   +------+'   +------+'   +------+'   +------+'   
                     .' |    .'| .' |    .'| .' |    .'| .' |    .'| .'…
                    """
                ).strip('\n'),
                method_name='canvasGeneratorImplementation(String, Filter)',
                duration='0.001s',
                result='passed',
                test_number=24,
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    """
                       .+------+
                     .' |    .'|
                    +---+--+'  |
                    |   |  |   |
                    |  ,+--+---+
                    |.'    | .' 
                    +------+', Filter(width=6, height=8, result=   .+------+   .+------+   .+------+   .+------+   .+------+   .+------+
                     .' |    .'| .' |    .'| .' |    .'| .' |    .'| .' |    .'| .' |    .'|
                    +---+--+'  |+---+--+'  |+---+--+'  |+---+--+'  |+---+--+'  |+---+--+'  |
                    |   |  |   ||   |  |   ||   |  |   ||   |  |   ||   |  |   ||   |  |   |
                    |  ,+--+---+|  ,+--+---+|  ,+--+---+|  ,+--+---+|  ,+--+---+|  ,+--+---+
                    |.'    | .' |.'    | .' |.'    | .' |.'    | .' |.'    | .' |.'    | .' 
                    +------+'   +------+'   +------+'   +---…
                    """
                ).strip('\n'),
                method_name='canvasGeneratorImplementation(String, Filter)',
                duration='0.002s',
                result='passed',
                test_number=25,
            ),
            TestData(
                class_name='Test',
                test='○, Filter(width=2, height=1, result=○○)',
                method_name='canvasGeneratorImplementation(String, Filter)',
                duration='0.001s',
                result='passed',
                test_number=2,
            ),
            TestData(
                class_name='Test',
                test=dedent(  # noqa: WPS462 Disabled because you can use multiline string with the dedent function
                    """
                    ○, Filter(width=1, height=2, result=○
                    ○)
                    """
                ).strip('\n'),
                method_name='canvasGeneratorImplementation(String, Filter)',
                duration='0s',
                result='passed',
                test_number=3,
            ),
            TestData(
                class_name='Test',
                test=dedent(  # noqa: WPS462 Disabled because you can use multiline string with the dedent function
                    """
                    ○, Filter(width=5, height=7, result=○○○○○
                    ○○○○○
                    ○○○○○
                    ○○○○○
                    ○○○○○
                    ○○○○○
                    ○○○○○)
                    """
                ).strip('\n'),
                method_name='canvasGeneratorImplementation(String, Filter)',
                duration='0s',
                result='passed',
                test_number=4,
            ),
            TestData(
                class_name='Test',
                test=dedent(  # noqa: WPS462 Disabled because you can use multiline string with the dedent function
                    """
                    ○, Filter(width=6, height=8, result=○○○○○○
                    ○○○○○○
                    ○○○○○○
                    ○○○○○○
                    ○○○○○○
                    ○○○○○○
                    ○○○○○○
                    ○○○○○○)
                    """
                ).strip('\n'),
                method_name='canvasGeneratorImplementation(String, Filter)',
                duration='0s',
                result='passed',
                test_number=5,
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                     X
                    / \
                    \ /
                     X, Filter(width=1, height=1, result= X 
                    / \
                    \ /
                     X )
                    """
                ).strip('\n'),
                method_name='canvasGeneratorImplementation(String, Filter)',
                duration='0s',
                result='passed',
                test_number=6,
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                     X
                    / \
                    \ /
                     X, Filter(width=2, height=1, result= X  X 
                    / \/ \
                    \ /\ /
                     X  X )
                    """
                ).strip('\n'),
                method_name='canvasGeneratorImplementation(String, Filter)',
                duration='0s',
                result='passed',
                test_number=7,
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                     X
                    / \
                    \ /
                     X, Filter(width=1, height=2, result= X 
                    / \
                    \ /
                     X 
                    / \
                    \ /
                     X )
                    """
                ).strip('\n'),
                method_name='canvasGeneratorImplementation(String, Filter)',
                duration='0.001s',
                result='passed',
                test_number=8,
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                     X
                    / \
                    \ /
                     X, Filter(width=5, height=7, result= X  X  X  X  X 
                    / \/ \/ \/ \/ \
                    \ /\ /\ /\ /\ /
                     X  X  X  X  X 
                    / \/ \/ \/ \/ \
                    \ /\ /\ /\ /\ /
                     X  X  X  X  X 
                    / \/ \/ \/ \/ \
                    \ /\ /\ /\ /\ /
                     X  X  X  X  X 
                    / \/ \/ \/ \/ \
                    \ /\ /\ /\ /\ /
                     X  X  X  X  X 
                    / \/ \/ \/ \/ \
                    \ /\ /\ /\ /\ /
                     X  X  X  X  X 
                    / \/ \/ \/ \/ \
                    \ /\ /\ /\ /\ /
                     X  X  X  X  X 
                    / \/ \/ \/ \/ \
                    \ /\ /\ /\ /\ /
                     X  X  X  X  X )
                    """
                ).strip('\n'),
                method_name='canvasGeneratorImplementation(String, Filter)',
                duration='0.001s',
                result='passed',
                test_number=9,
            ),
            TestData(
                class_name='Test',
                test='fillPatternRowErrorCase()',
                method_name='fillPatternRowErrorCase()',
                duration='0.001s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test='fillPatternRowFunction()',
                method_name='fillPatternRowFunction()',
                duration='0s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test=', 5,      ',
                method_name='fillPatternRowImplementation(String, int, String)',
                duration='0.026s',
                result='passed',
                test_number=1,
            ),
            TestData(
                class_name='Test',
                test='○, 5, ○    ',
                method_name='fillPatternRowImplementation(String, int, String)',
                duration='0.001s',
                result='passed',
                test_number=2,
            ),
            TestData(
                class_name='Test',
                test='○○, 5, ○○   ',
                method_name='fillPatternRowImplementation(String, int, String)',
                duration='0.001s',
                result='passed',
                test_number=3,
            ),
            TestData(
                class_name='Test',
                test='○○○, 5, ○○○  ',
                method_name='fillPatternRowImplementation(String, int, String)',
                duration='0s',
                result='passed',
                test_number=4,
            ),
            TestData(
                class_name='Test',
                test='○○○○, 5, ○○○○ ',
                method_name='fillPatternRowImplementation(String, int, String)',
                duration='0.001s',
                result='passed',
                test_number=5,
            ),
            TestData(
                class_name='Test',
                test='○○○○○, 5, ○○○○○',
                method_name='fillPatternRowImplementation(String, int, String)',
                duration='0.001s',
                result='passed',
                test_number=6,
            ),
            TestData(
                class_name='Test',
                test='getPatternHeightFunction()',
                method_name='getPatternHeightFunction()',
                duration='0s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test='○, 1',
                method_name='getPatternHeightImplementation(String, int)',
                duration='0.006s',
                result='passed',
                test_number=1,
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                     X
                    / \
                    \ /
                     X, 4
                    """
                ).strip('\n'),
                method_name='getPatternHeightImplementation(String, int)',
                duration='0s',
                result='passed',
                test_number=2,
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                      ____   
                     /    \
                    / /  \ \
                    \ \__/ /
                     \____/, 5
                    """
                ).strip('\n'),
                method_name='getPatternHeightImplementation(String, int)',
                duration='0s',
                result='passed',
                test_number=3,
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    """
                    +---+---+
                    | o   o |
                    |   ^   |
                    |  ---  |
                    +---+---+, 5
                    """
                ).strip('\n'),
                method_name='getPatternHeightImplementation(String, int)',
                duration='0.001s',
                result='passed',
                test_number=4,
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    """
                       .+------+
                     .' |    .'|
                    +---+--+'  |
                    |   |  |   |
                    |  ,+--+---+
                    |.'    | .' 
                    +------+', 7
                    """
                ).strip('\n'),
                method_name='getPatternHeightImplementation(String, int)',
                duration='0.001s',
                result='passed',
                test_number=5,
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
