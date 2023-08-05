from textwrap import dedent

import pytest
from typing import List

from pathlib import Path

from jba.models.edu_logs import ExceptionData, TestData
from jba.test_logs.parsers import parse_gradle_stderr_logs, parse_gradle_test_logs
from jba_tests.test_logs import TEST_LOGS_FOLDER

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
                    [10]  X
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
                ).strip(),
                method_name='canvasGeneratorImplementation(String, Filter)[10]',
                duration='0.001s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                    [11]   ____   
                     /    \
                    / /  \ \
                    \ \__/ /
                     \____/, Filter(width=1, height=1, result=  ____   
                     /    \  
                    / /  \ \ 
                    \ \__/ / 
                     \____/  )
                    """
                ).strip(),
                method_name='canvasGeneratorImplementation(String, Filter)[11]',
                duration='0.001s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                    [12]   ____   
                     /    \
                    / /  \ \
                    \ \__/ /
                     \____/, Filter(width=2, height=1, result=  ____     ____   
                     /    \   /    \  
                    / /  \ \ / /  \ \ 
                    \ \__/ / \ \__/ / 
                     \____/   \____/  )
                    """
                ).strip(),
                method_name='canvasGeneratorImplementation(String, Filter)[12]',
                duration='0.001s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                    [13]   ____   
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
                ).strip(),
                method_name='canvasGeneratorImplementation(String, Filter)[13]',
                duration='0.004s',
                result='failed',
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
                ).strip(),
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                    [14]   ____   
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
                ).strip(),
                method_name='canvasGeneratorImplementation(String, Filter)[14]',
                duration='0.002s',
                result='failed',
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
                ).strip(),
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                    [15]   ____   
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
                ).strip(),
                method_name='canvasGeneratorImplementation(String, Filter)[15]',
                duration='0.002s',
                result='failed',
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
                ).strip(),
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                    [16] +---+---+
                    | o   o |
                    |   ^   |
                    |  ---  |
                    +---+---+, Filter(width=1, height=1, result=+---+---+
                    | o   o |
                    |   ^   |
                    |  ---  |
                    +---+---+)
                    """
                ).strip(),
                method_name='canvasGeneratorImplementation(String, Filter)[16]',
                duration='0s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                    [17] +---+---+
                    | o   o |
                    |   ^   |
                    |  ---  |
                    +---+---+, Filter(width=2, height=1, result=+---+---++---+---+
                    | o   o || o   o |
                    |   ^   ||   ^   |
                    |  ---  ||  ---  |
                    +---+---++---+---+)
                    """
                ).strip(),
                method_name='canvasGeneratorImplementation(String, Filter)[17]',
                duration='0s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                    [18] +---+---+
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
                ).strip(),
                method_name='canvasGeneratorImplementation(String, Filter)[18]',
                duration='0.001s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                    [19] +---+---+
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
                ).strip(),
                method_name='canvasGeneratorImplementation(String, Filter)[19]',
                duration='0.001s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test='[1] ○, Filter(width=1, height=1, result=○)',
                method_name='canvasGeneratorImplementation(String, Filter)[1]',
                duration='0.004s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                    [20] +---+---+
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
                ).strip(),
                method_name='canvasGeneratorImplementation(String, Filter)[20]',
                duration='0.001s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                    [21]    .+------+
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
                ).strip(),
                method_name='canvasGeneratorImplementation(String, Filter)[21]',
                duration='0.001s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                    [22]    .+------+
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
                ).strip(),
                method_name='canvasGeneratorImplementation(String, Filter)[22]',
                duration='0.001s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                    [23]    .+------+
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
                ).strip(),
                method_name='canvasGeneratorImplementation(String, Filter)[23]',
                duration='0s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                    [24]    .+------+
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
                ).strip(),
                method_name='canvasGeneratorImplementation(String, Filter)[24]',
                duration='0.001s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                    [25]    .+------+
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
                ).strip(),
                method_name='canvasGeneratorImplementation(String, Filter)[25]',
                duration='0.002s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test='[2] ○, Filter(width=2, height=1, result=○○)',
                method_name='canvasGeneratorImplementation(String, Filter)[2]',
                duration='0.001s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    """
                    [3] ○, Filter(width=1, height=2, result=○
                    ○)
                    """
                ).strip(),
                method_name='canvasGeneratorImplementation(String, Filter)[3]',
                duration='0s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    """
                    [4] ○, Filter(width=5, height=7, result=○○○○○
                    ○○○○○
                    ○○○○○
                    ○○○○○
                    ○○○○○
                    ○○○○○
                    ○○○○○)
                    """
                ).strip(),
                method_name='canvasGeneratorImplementation(String, Filter)[4]',
                duration='0s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    """
                    [5] ○, Filter(width=6, height=8, result=○○○○○○
                    ○○○○○○
                    ○○○○○○
                    ○○○○○○
                    ○○○○○○
                    ○○○○○○
                    ○○○○○○
                    ○○○○○○)
                    """
                ).strip(),
                method_name='canvasGeneratorImplementation(String, Filter)[5]',
                duration='0s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                    [6]  X
                    / \
                    \ /
                     X, Filter(width=1, height=1, result= X 
                    / \
                    \ /
                     X )
                    """
                ).strip(),
                method_name='canvasGeneratorImplementation(String, Filter)[6]',
                duration='0s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                    [7]  X
                    / \
                    \ /
                     X, Filter(width=2, height=1, result= X  X 
                    / \/ \
                    \ /\ /
                     X  X )
                    """
                ).strip(),
                method_name='canvasGeneratorImplementation(String, Filter)[7]',
                duration='0s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                    [8]  X
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
                ).strip(),
                method_name='canvasGeneratorImplementation(String, Filter)[8]',
                duration='0.001s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                    [9]  X
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
                ).strip(),
                method_name='canvasGeneratorImplementation(String, Filter)[9]',
                duration='0.001s',
                result='passed',
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
                test='[1] , 5,      ',
                method_name='fillPatternRowImplementation(String, int, String)[1]',
                duration='0.026s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test='[2] ○, 5, ○    ',
                method_name='fillPatternRowImplementation(String, int, String)[2]',
                duration='0.001s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test='[3] ○○, 5, ○○   ',
                method_name='fillPatternRowImplementation(String, int, String)[3]',
                duration='0.001s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test='[4] ○○○, 5, ○○○  ',
                method_name='fillPatternRowImplementation(String, int, String)[4]',
                duration='0s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test='[5] ○○○○, 5, ○○○○ ',
                method_name='fillPatternRowImplementation(String, int, String)[5]',
                duration='0.001s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test='[6] ○○○○○, 5, ○○○○○',
                method_name='fillPatternRowImplementation(String, int, String)[6]',
                duration='0.001s',
                result='passed',
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
                test='[1] ○, 1',
                method_name='getPatternHeightImplementation(String, int)[1]',
                duration='0.006s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                    [2]  X
                    / \
                    \ /
                     X, 4
                    """
                ).strip(),
                method_name='getPatternHeightImplementation(String, int)[2]',
                duration='0s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                    [3]   ____   
                     /    \
                    / /  \ \
                    \ \__/ /
                     \____/, 5
                    """
                ).strip(),
                method_name='getPatternHeightImplementation(String, int)[3]',
                duration='0s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                    [4] +---+---+
                    | o   o |
                    |   ^   |
                    |  ---  |
                    +---+---+, 5
                    """
                ).strip(),
                method_name='getPatternHeightImplementation(String, int)[4]',
                duration='0.001s',
                result='passed',
            ),
            TestData(
                class_name='Test',
                test=dedent(
                    r"""
                    [5]    .+------+
                     .' |    .'|
                    +---+--+'  |
                    |   |  |   |
                    |  ,+--+---+
                    |.'    | .' 
                    +------+', 7
                    """
                ).strip(),
                method_name='getPatternHeightImplementation(String, int)[5]',
                duration='0.001s',
                result='passed',
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
