from typing import List, Optional, Tuple

import pandas as pd
import pytest
from pandas._testing import assert_frame_equal

from jba.src.models.edu_columns import EduColumnName
from jba.src.models.edu_logs import TestResult, TestData, TestDataField
from jba.src.visualization.common import (
    _convert_to_timeline,
    TimelineItem,
    _find_test_result,
    _get_aggregated_result,
    convert_tests_to_timeline,
    START_COLUMN,
    FINISH_COLUMN,
    aggregate_tests_timeline,
)

CONVERT_TO_TIMELINE_DATA = [
    ([], []),
    (['A'], [('A', 1, 1)]),
    (['A', 'A', 'A'], [('A', 1, 3)]),
    (['A', 'B'], [('A', 1, 1), ('B', 2, 2)]),
    (['A', 'B', 'C', 'A', 'B', 'C'], [('A', 1, 1), ('B', 2, 2), ('C', 3, 3), ('A', 4, 4), ('B', 5, 5), ('C', 6, 6)]),
    ([None, 'A', 'A', 'A', 'B'], [(None, 1, 1), ('A', 2, 4), ('B', 5, 5)]),
    (
        [None, None, 'A', 'A', 'B', None, None, None, 'B', 'C', 'D', 'D', 'D', None, None],
        [
            (None, 1, 2),
            ('A', 3, 4),
            ('B', 5, 5),
            (None, 6, 8),
            ('B', 9, 9),
            ('C', 10, 10),
            ('D', 11, 13),
            (None, 14, 15),
        ],
    ),
]


@pytest.mark.parametrize(('elements', 'expected_timeline'), CONVERT_TO_TIMELINE_DATA)
def test_convert_to_timeline(elements: List[Optional[str]], expected_timeline: List[TimelineItem]):
    assert _convert_to_timeline(elements) == expected_timeline


COMMON_TESTS = [
    TestData(
        class_name='Test',
        method_name='some_passed_test()',
        test='some_passed_test()',
        duration='0.0001s',
        result=TestResult.PASSED,
    ),
    TestData(
        class_name='Test',
        method_name='some_passed_parametrized_test(String)',
        test='A',
        duration='0.0001s',
        result=TestResult.PASSED,
        test_number=1,
    ),
    TestData(
        class_name='Test',
        method_name='some_passed_parametrized_test(String)',
        test='B',
        duration='0.0001s',
        result=TestResult.PASSED,
        test_number=2,
    ),
    TestData(
        class_name='Test',
        method_name='some_passed_parametrized_test(String)',
        test='C',
        duration='0.0001s',
        result=TestResult.PASSED,
        test_number=3,
    ),
    TestData(
        class_name='Test',
        method_name='some_failed_test()',
        test='some_failed_test()',
        duration='0.0001s',
        result=TestResult.FAILED,
        error_class='some_error_class',
        message='some error message',
    ),
    TestData(
        class_name='Test',
        method_name='some_all_failed_parametrized_test(String)',
        test='A',
        duration='0.0001s',
        result=TestResult.FAILED,
        test_number=1,
        error_class='some_error_class',
        message='some error message',
    ),
    TestData(
        class_name='Test',
        method_name='some_all_failed_parametrized_test(String)',
        test='B',
        duration='0.0001s',
        result=TestResult.FAILED,
        test_number=2,
        error_class='some_error_class',
        message='some error message',
    ),
    TestData(
        class_name='Test',
        method_name='some_all_failed_parametrized_test(String)',
        test='C',
        duration='0.0001s',
        result=TestResult.FAILED,
        test_number=3,
        error_class='some_error_class',
        message='some error message',
    ),
    TestData(
        class_name='Test',
        method_name='some_partial_failed_parametrized_test(String)',
        test='A',
        duration='0.0001s',
        result=TestResult.FAILED,
        test_number=1,
        error_class='some_error_class',
        message='some error message',
    ),
    TestData(
        class_name='Test',
        method_name='some_partial_failed_parametrized_test(String)',
        test='B',
        duration='0.0001s',
        result=TestResult.PASSED,
        test_number=2,
    ),
    TestData(
        class_name='Test',
        method_name='some_partial_failed_parametrized_test(String)',
        test='C',
        duration='0.0001s',
        result=TestResult.FAILED,
        test_number=3,
        error_class='some_error_class',
        message='some error message',
    ),
    TestData(
        class_name='Test',
        method_name='some_ignored_test()',
        test='some_ignored_test()',
        duration='0.0001s',
        result=TestResult.IGNORED,
    ),
    TestData(
        class_name='Test',
        method_name='some_all_ignored_parametrized_test(String)',
        test='A',
        duration='0.0001s',
        result=TestResult.IGNORED,
        test_number=1,
    ),
    TestData(
        class_name='Test',
        method_name='some_all_ignored_parametrized_test(String)',
        test='B',
        duration='0.0001s',
        result=TestResult.IGNORED,
        test_number=2,
    ),
    TestData(
        class_name='Test',
        method_name='some_all_ignored_parametrized_test(String)',
        test='C',
        duration='0.0001s',
        result=TestResult.IGNORED,
        test_number=3,
    ),
    TestData(
        class_name='Test',
        method_name='some_partial_ignored_parametrized_test(String)',
        test='A',
        duration='0.0001s',
        result=TestResult.FAILED,
        test_number=1,
        error_class='some_error_class',
        message='some error message',
    ),
    TestData(
        class_name='Test',
        method_name='some_partial_ignored_parametrized_test(String)',
        test='B',
        duration='0.0001s',
        result=TestResult.IGNORED,
        test_number=2,
    ),
    TestData(
        class_name='Test',
        method_name='some_partial_ignored_parametrized_test(String)',
        test='C',
        duration='0.0001s',
        result=TestResult.PASSED,
        test_number=3,
    ),
]


def test_find_test_result():
    for test in COMMON_TESTS:
        assert _find_test_result(test.class_name, test.method_name, test.test_number, COMMON_TESTS) == test.result


FIND_TEST_RESULT_DATA = [
    ('Test', 'some_test()', None, [], None),
    ('Test', 'some_parametrized_test()', 42, [], None),
    (
        'Test',
        'some_nonexistent_test()',
        None,
        [
            TestData(
                class_name='Test',
                method_name='some_test()',
                test='some_test()',
                duration='0.0001s',
                result=TestResult.PASSED,
            ),
            TestData(
                class_name='Test',
                method_name='some_parametrized_test(String)',
                test='A',
                duration='0.0001s',
                result=TestResult.PASSED,
                test_number=1,
            ),
            TestData(
                class_name='Test',
                method_name='some_parametrized_test(String)',
                test='B',
                duration='0.0001s',
                result=TestResult.PASSED,
                test_number=2,
            ),
        ],
        None,
    ),
    (
        'Test',
        'some_parametrized_test()',
        42,
        [
            TestData(
                class_name='Test',
                method_name='some_test()',
                test='some_test()',
                duration='0.0001s',
                result=TestResult.PASSED,
            ),
            TestData(
                class_name='Test',
                method_name='some_parametrized_test(String)',
                test='A',
                duration='0.0001s',
                result=TestResult.PASSED,
                test_number=1,
            ),
            TestData(
                class_name='Test',
                method_name='some_parametrized_test(String)',
                test='B',
                duration='0.0001s',
                result=TestResult.PASSED,
                test_number=2,
            ),
        ],
        None,
    ),
    (
        'Test',
        'some_test()',
        None,
        [
            TestData(
                class_name='Test',
                method_name='some_test()',
                test='some_test()',
                duration='0.0001s',
                result=TestResult.FAILED,
                error_class='some_error_class',
                message='some error message',
            ),
            TestData(
                class_name='Test',
                method_name='some_test()',
                test='some_test()',
                duration='0.0001s',
                result=TestResult.PASSED,
            ),
        ],
        TestResult.FAILED,
    ),
    (
        'Test',
        'some_parametrized_test(String)',
        1,
        [
            TestData(
                class_name='Test',
                method_name='some_parametrized_test(String)',
                test='A',
                duration='0.0001s',
                result=TestResult.FAILED,
                error_class='some_error_class',
                message='some error message',
                test_number=1,
            ),
            TestData(
                class_name='Test',
                method_name='some_parametrized_test(String)',
                test='A',
                duration='0.0001s',
                result=TestResult.PASSED,
                test_number=1,
            ),
        ],
        TestResult.FAILED,
    ),
]


@pytest.mark.parametrize(
    ('class_name', 'method_name', 'test_number', 'tests', 'expected_test_result'),
    FIND_TEST_RESULT_DATA,
)
def test_find_test_result_edge_cases(
    class_name: str,
    method_name: str,
    test_number: Optional[int],
    tests: List[TestData],
    expected_test_result: Optional[TestResult],
):
    assert _find_test_result(class_name, method_name, test_number, tests) == expected_test_result


CONVERT_TESTS_TO_TIMELINE_DATA = [
    ([], []),
    (
        [
            [
                TestData(
                    class_name='Test',
                    method_name='some_test()',
                    test='some_test()',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='A',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=1,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='B',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=2,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='C',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=3,
                ),
            ],
            [
                TestData(
                    class_name='Test',
                    method_name='some_test()',
                    test='some_test()',
                    duration='0.0001s',
                    result=TestResult.FAILED,
                    error_class='some_error_class',
                    message='some error message',
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='A',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=1,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='B',
                    duration='0.0001s',
                    result=TestResult.FAILED,
                    test_number=2,
                    error_class='some_error_class',
                    message='some error message',
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='C',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=3,
                ),
            ],
            [
                TestData(
                    class_name='Test',
                    method_name='some_test()',
                    test='some_test()',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='A',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=1,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='B',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=2,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='C',
                    duration='0.0001s',
                    result=TestResult.FAILED,
                    test_number=3,
                    error_class='some_error_class',
                    message='some error message',
                ),
            ],
            [
                TestData(
                    class_name='Test',
                    method_name='some_test()',
                    test='some_test()',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='A',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=1,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='B',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=2,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='C',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=3,
                ),
            ],
        ],
        [
            ('Test', 'some_test()', None, TestResult.PASSED, 1, 1),
            ('Test', 'some_test()', None, TestResult.FAILED, 2, 2),
            ('Test', 'some_test()', None, TestResult.PASSED, 3, 4),
            ('Test', 'some_parametrized_test(String)', 1, TestResult.PASSED, 1, 4),
            ('Test', 'some_parametrized_test(String)', 2, TestResult.PASSED, 1, 1),
            ('Test', 'some_parametrized_test(String)', 2, TestResult.FAILED, 2, 2),
            ('Test', 'some_parametrized_test(String)', 2, TestResult.PASSED, 3, 4),
            ('Test', 'some_parametrized_test(String)', 3, TestResult.PASSED, 1, 2),
            ('Test', 'some_parametrized_test(String)', 3, TestResult.FAILED, 3, 3),
            ('Test', 'some_parametrized_test(String)', 3, TestResult.PASSED, 4, 4),
        ],
    ),
    (
        [
            [
                TestData(
                    class_name='Test',
                    method_name='some_test()',
                    test='some_test()',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='A',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=1,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='B',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=2,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='C',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=3,
                ),
            ],
            [
                TestData(
                    class_name='Test',
                    method_name='some_test()',
                    test='some_test()',
                    duration='0.0001s',
                    result=TestResult.FAILED,
                    error_class='some_error_class',
                    message='some error message',
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='A',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=1,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='B',
                    duration='0.0001s',
                    result=TestResult.FAILED,
                    test_number=2,
                    error_class='some_error_class',
                    message='some error message',
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='C',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=3,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_unexpected_test()',
                    test='some_unexpected_test()',
                    duration='0.0001s',
                    result=TestResult.FAILED,
                    error_class='some_error_class',
                    message='some error message',
                ),
            ],
            [
                TestData(
                    class_name='Test',
                    method_name='some_test()',
                    test='some_test()',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='A',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=1,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='B',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=2,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='C',
                    duration='0.0001s',
                    result=TestResult.FAILED,
                    test_number=3,
                    error_class='some_error_class',
                    message='some error message',
                ),
                TestData(
                    class_name='Test',
                    method_name='some_unexpected_test()',
                    test='some_unexpected_test()',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_unexpected_parametrized_test(String)',
                    test='A',
                    duration='0.0001s',
                    result=TestResult.FAILED,
                    test_number=1,
                    error_class='some_error_class',
                    message='some error message',
                ),
                TestData(
                    class_name='Test',
                    method_name='some_unexpected_parametrized_test(String)',
                    test='B',
                    duration='0.0001s',
                    result=TestResult.FAILED,
                    test_number=2,
                    error_class='some_error_class',
                    message='some error message',
                ),
            ],
            [
                TestData(
                    class_name='Test',
                    method_name='some_test()',
                    test='some_test()',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='A',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=1,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='B',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=2,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='C',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=3,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_unexpected_parametrized_test(String)',
                    test='A',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=1,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_unexpected_parametrized_test(String)',
                    test='B',
                    duration='0.0001s',
                    result=TestResult.FAILED,
                    test_number=2,
                    error_class='some_error_class',
                    message='some error message',
                ),
            ],
        ],
        [
            ('Test', 'some_test()', None, TestResult.PASSED, 1, 1),
            ('Test', 'some_test()', None, TestResult.FAILED, 2, 2),
            ('Test', 'some_test()', None, TestResult.PASSED, 3, 4),
            ('Test', 'some_parametrized_test(String)', 1, TestResult.PASSED, 1, 4),
            ('Test', 'some_parametrized_test(String)', 2, TestResult.PASSED, 1, 1),
            ('Test', 'some_parametrized_test(String)', 2, TestResult.FAILED, 2, 2),
            ('Test', 'some_parametrized_test(String)', 2, TestResult.PASSED, 3, 4),
            ('Test', 'some_parametrized_test(String)', 3, TestResult.PASSED, 1, 2),
            ('Test', 'some_parametrized_test(String)', 3, TestResult.FAILED, 3, 3),
            ('Test', 'some_parametrized_test(String)', 3, TestResult.PASSED, 4, 4),
            ('Test', 'some_unexpected_test()', None, TestResult.FAILED, 2, 2),
            ('Test', 'some_unexpected_test()', None, TestResult.PASSED, 3, 3),
            ('Test', 'some_unexpected_parametrized_test(String)', 1, TestResult.FAILED, 3, 3),
            ('Test', 'some_unexpected_parametrized_test(String)', 1, TestResult.PASSED, 4, 4),
            ('Test', 'some_unexpected_parametrized_test(String)', 2, TestResult.FAILED, 3, 4),
        ],
    ),
    (
        [
            None,
            None,
            [
                TestData(
                    class_name='Test',
                    method_name='some_test()',
                    test='some_test()',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='A',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=1,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='B',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=2,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='C',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=3,
                ),
            ],
            [
                TestData(
                    class_name='Test',
                    method_name='some_test()',
                    test='some_test()',
                    duration='0.0001s',
                    result=TestResult.FAILED,
                    error_class='some_error_class',
                    message='some error message',
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='A',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=1,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='B',
                    duration='0.0001s',
                    result=TestResult.FAILED,
                    test_number=2,
                    error_class='some_error_class',
                    message='some error message',
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='C',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=3,
                ),
            ],
            [
                TestData(
                    class_name='Test',
                    method_name='some_test()',
                    test='some_test()',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='A',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=1,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='B',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=2,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='C',
                    duration='0.0001s',
                    result=TestResult.FAILED,
                    test_number=3,
                    error_class='some_error_class',
                    message='some error message',
                ),
            ],
            None,
            [
                TestData(
                    class_name='Test',
                    method_name='some_test()',
                    test='some_test()',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='A',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=1,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='B',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=2,
                ),
                TestData(
                    class_name='Test',
                    method_name='some_parametrized_test(String)',
                    test='C',
                    duration='0.0001s',
                    result=TestResult.PASSED,
                    test_number=3,
                ),
            ],
            None,
        ],
        [
            ('Test', 'some_test()', None, TestResult.PASSED, 3, 3),
            ('Test', 'some_test()', None, TestResult.FAILED, 4, 4),
            ('Test', 'some_test()', None, TestResult.PASSED, 5, 5),
            ('Test', 'some_test()', None, TestResult.PASSED, 7, 7),
            ('Test', 'some_parametrized_test(String)', 1, TestResult.PASSED, 3, 5),
            ('Test', 'some_parametrized_test(String)', 1, TestResult.PASSED, 7, 7),
            ('Test', 'some_parametrized_test(String)', 2, TestResult.PASSED, 3, 3),
            ('Test', 'some_parametrized_test(String)', 2, TestResult.FAILED, 4, 4),
            ('Test', 'some_parametrized_test(String)', 2, TestResult.PASSED, 5, 5),
            ('Test', 'some_parametrized_test(String)', 2, TestResult.PASSED, 7, 7),
            ('Test', 'some_parametrized_test(String)', 3, TestResult.PASSED, 3, 4),
            ('Test', 'some_parametrized_test(String)', 3, TestResult.FAILED, 5, 5),
            ('Test', 'some_parametrized_test(String)', 3, TestResult.PASSED, 7, 7),
        ],
    ),
]


@pytest.mark.parametrize(('tests', 'expected_timeline_data'), CONVERT_TESTS_TO_TIMELINE_DATA)
def test_convert_tests_to_timeline(  # noqa: WPS234
    tests: List[Optional[List[TestData]]],
    expected_timeline_data: List[Tuple],
):
    group_data = pd.DataFrame(
        map(lambda x: None if x is None else TestData.schema().dumps(x, many=True), tests),
        columns=[EduColumnName.TESTS.value],
    )

    sort_by = [
        TestDataField.CLASS_NAME.value,
        TestDataField.METHOD_NAME.value,
        TestDataField.TEST_NUMBER.value,
    ]

    actual_timeline = convert_tests_to_timeline(group_data).sort_values(by=sort_by).reset_index(drop=True)
    expected_timeline = (
        pd.DataFrame(
            expected_timeline_data,
            columns=[
                TestDataField.CLASS_NAME.value,
                TestDataField.METHOD_NAME.value,
                TestDataField.TEST_NUMBER.value,
                TestDataField.RESULT.value,
                START_COLUMN,
                FINISH_COLUMN,
            ],
        )
        .sort_values(by=sort_by)
        .reset_index(drop=True)
    )

    assert_frame_equal(actual_timeline, expected_timeline)


GET_AGGREGATED_RESULT_DATA = [
    ([], None),
    ([TestResult.PASSED], TestResult.PASSED),
    ([TestResult.FAILED], TestResult.FAILED),
    ([TestResult.IGNORED], TestResult.IGNORED),
    ([TestResult.PASSED, TestResult.PASSED, TestResult.PASSED], TestResult.PASSED),
    ([TestResult.PASSED, TestResult.FAILED, TestResult.PASSED], TestResult.FAILED),
    ([TestResult.PASSED, TestResult.FAILED, TestResult.IGNORED], TestResult.FAILED),
    ([TestResult.PASSED, TestResult.IGNORED, TestResult.PASSED], TestResult.IGNORED),
    ([TestResult.FAILED, TestResult.FAILED, TestResult.IGNORED], TestResult.FAILED),
    ([TestResult.IGNORED, TestResult.IGNORED, TestResult.IGNORED], TestResult.IGNORED),
]


@pytest.mark.parametrize(('test_results', 'expected_result'), GET_AGGREGATED_RESULT_DATA)
def test_get_aggregated_result(test_results: List[TestResult], expected_result: Optional[TestResult]):
    assert _get_aggregated_result(test_results) == expected_result


AGGREGATE_TESTS_TIMELINE_DATA = [
    ([], []),
    (
        [
            ('Test', 'some_test_1()', None, TestResult.FAILED, 1, 2),
            ('Test', 'some_test_1()', None, TestResult.PASSED, 3, 4),
            ('Test', 'some_test_2()', None, TestResult.FAILED, 1, 4),
            ('Test', 'some_test_3()', None, TestResult.IGNORED, 2, 3),
        ],
        [
            ('Test', 'some_test_1()', None, TestResult.FAILED, 1, 2),
            ('Test', 'some_test_1()', None, TestResult.PASSED, 3, 4),
            ('Test', 'some_test_2()', None, TestResult.FAILED, 1, 4),
            ('Test', 'some_test_3()', None, TestResult.IGNORED, 2, 3),
        ],
    ),
    (
        [
            ('Test', 'some_parametrized_test_1(String)', 1, TestResult.PASSED, 1, 3),
            ('Test', 'some_parametrized_test_1(String)', 2, TestResult.FAILED, 1, 1),
            ('Test', 'some_parametrized_test_1(String)', 2, TestResult.PASSED, 2, 3),
            ('Test', 'some_parametrized_test_1(String)', 3, TestResult.PASSED, 1, 2),
            ('Test', 'some_parametrized_test_1(String)', 3, TestResult.FAILED, 3, 3),
            ('Test', 'some_parametrized_test_2(String)', 1, TestResult.PASSED, 1, 3),
            ('Test', 'some_parametrized_test_2(String)', 2, TestResult.IGNORED, 1, 1),
            ('Test', 'some_parametrized_test_3(String)', 1, TestResult.PASSED, 1, 3),
            ('Test', 'some_parametrized_test_3(String)', 2, TestResult.PASSED, 1, 3),
            ('Test', 'some_parametrized_test_3(String)', 3, TestResult.PASSED, 1, 3),
        ],
        [
            ('Test', 'some_parametrized_test_1(String)', None, TestResult.FAILED, 1, 1),
            ('Test', 'some_parametrized_test_1(String)', None, TestResult.PASSED, 2, 2),
            ('Test', 'some_parametrized_test_1(String)', None, TestResult.FAILED, 3, 3),
            ('Test', 'some_parametrized_test_2(String)', None, TestResult.IGNORED, 1, 1),
            ('Test', 'some_parametrized_test_2(String)', None, TestResult.PASSED, 2, 3),
            ('Test', 'some_parametrized_test_3(String)', None, TestResult.PASSED, 1, 3),
        ],
    ),
    (
        [
            ('Test', 'some_test_1()', None, TestResult.FAILED, 1, 2),
            ('Test', 'some_test_1()', None, TestResult.PASSED, 3, 4),
            ('Test', 'some_test_2()', None, TestResult.FAILED, 1, 4),
            ('Test', 'some_test_3()', None, TestResult.IGNORED, 2, 3),
            ('Test', 'some_parametrized_test_1(String)', 1, TestResult.PASSED, 1, 3),
            ('Test', 'some_parametrized_test_1(String)', 2, TestResult.FAILED, 1, 1),
            ('Test', 'some_parametrized_test_1(String)', 2, TestResult.PASSED, 2, 3),
            ('Test', 'some_parametrized_test_1(String)', 3, TestResult.PASSED, 1, 2),
            ('Test', 'some_parametrized_test_1(String)', 3, TestResult.FAILED, 3, 3),
            ('Test', 'some_parametrized_test_2(String)', 1, TestResult.PASSED, 1, 3),
            ('Test', 'some_parametrized_test_2(String)', 2, TestResult.IGNORED, 1, 1),
            ('Test', 'some_parametrized_test_3(String)', 1, TestResult.PASSED, 1, 3),
            ('Test', 'some_parametrized_test_3(String)', 2, TestResult.PASSED, 1, 3),
            ('Test', 'some_parametrized_test_3(String)', 3, TestResult.PASSED, 1, 3),
        ],
        [
            ('Test', 'some_test_1()', None, TestResult.FAILED, 1, 2),
            ('Test', 'some_test_1()', None, TestResult.PASSED, 3, 4),
            ('Test', 'some_test_2()', None, TestResult.FAILED, 1, 4),
            ('Test', 'some_test_3()', None, TestResult.IGNORED, 2, 3),
            ('Test', 'some_parametrized_test_1(String)', None, TestResult.FAILED, 1, 1),
            ('Test', 'some_parametrized_test_1(String)', None, TestResult.PASSED, 2, 2),
            ('Test', 'some_parametrized_test_1(String)', None, TestResult.FAILED, 3, 3),
            ('Test', 'some_parametrized_test_2(String)', None, TestResult.IGNORED, 1, 1),
            ('Test', 'some_parametrized_test_2(String)', None, TestResult.PASSED, 2, 3),
            ('Test', 'some_parametrized_test_3(String)', None, TestResult.PASSED, 1, 3),
        ],
    ),
    (
        [
            ('Test', 'some_test()', None, TestResult.FAILED, 2, 2),
            ('Test', 'some_test()', None, TestResult.PASSED, 3, 4),
            ('Test', 'some_parametrized_test(String)', 1, TestResult.PASSED, 2, 3),
            ('Test', 'some_parametrized_test(String)', 2, TestResult.PASSED, 2, 3),
            ('Test', 'some_parametrized_test(String)', 3, TestResult.FAILED, 2, 2),
            ('Test', 'some_parametrized_test(String)', 3, TestResult.PASSED, 3, 3),
        ],
        [
            ('Test', 'some_test()', None, TestResult.FAILED, 2, 2),
            ('Test', 'some_test()', None, TestResult.PASSED, 3, 4),
            ('Test', 'some_parametrized_test(String)', None, TestResult.FAILED, 2, 2),
            ('Test', 'some_parametrized_test(String)', None, TestResult.PASSED, 3, 3),
        ],
    ),
]


@pytest.mark.parametrize(
    ('tests_timeline_data', 'expected_aggregate_tests_timeline_data'),
    AGGREGATE_TESTS_TIMELINE_DATA,
)
def test_aggregate_tests_timeline(
    tests_timeline_data: List[Tuple],
    expected_aggregate_tests_timeline_data: List[Tuple],
):
    tests_timeline = pd.DataFrame(
        tests_timeline_data,
        columns=[
            TestDataField.CLASS_NAME.value,
            TestDataField.METHOD_NAME.value,
            TestDataField.TEST_NUMBER.value,
            TestDataField.RESULT.value,
            START_COLUMN,
            FINISH_COLUMN,
        ],
    )

    expected_aggregate_tests_timeline = pd.DataFrame(
        expected_aggregate_tests_timeline_data,
        columns=[
            TestDataField.CLASS_NAME.value,
            TestDataField.METHOD_NAME.value,
            TestDataField.TEST_NUMBER.value,
            TestDataField.RESULT.value,
            START_COLUMN,
            FINISH_COLUMN,
        ],
    )

    actual_aggregate_tests_timeline = aggregate_tests_timeline(tests_timeline)

    assert_frame_equal(actual_aggregate_tests_timeline, expected_aggregate_tests_timeline)
