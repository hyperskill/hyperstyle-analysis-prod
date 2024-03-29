import itertools
from typing import Sequence, List, Optional, TypeVar, Tuple

import pandas as pd

from jba.src.models.edu_columns import EduColumnName
from jba.src.models.edu_logs import TestData, TestResult, TestDataField

T = TypeVar('T')

# element, start, finish
TimelineItem = Tuple[T, int, int]

START_COLUMN = 'start'
FINISH_COLUMN = 'finish'


def _convert_to_timeline(elements: Sequence[T]) -> List[TimelineItem]:
    """
    Convert an element sequence to a timeline.
    A timeline is a list of tuples, each consisting of an element, start index, and finish index.

    Index numbering starts from 1.

    :param elements: Elements to convert.
    :return: List of tuples (element, start index, finish index).
    """
    timeline = []

    current_position = 1
    for element, group in itertools.groupby(elements):
        group_len = len(list(group))
        timeline.append((element, current_position, current_position + group_len - 1))
        current_position += group_len

    return timeline


def _find_test_result(
    class_name: str,
    method_name: str,
    test_number: Optional[int],
    tests: List[TestData],
) -> Optional[TestResult]:
    """
    Find first test in the tests list by fields and return its result.

    :param class_name: Name of a test class to search.
    :param method_name: Name of a test method to search.
    :param test_number: Number of a parametrized test to search. Might be None.
    :param tests: List of tests to search for.
    :return: Result of the test which corresponding fields match `class_name`, `method_name` and `test_number`.
        If there is no such test, None will be returned.
    """
    try:
        return next(
            test
            for test in tests
            if test.class_name == class_name and test.method_name == method_name and test.test_number == test_number
        ).result
    except StopIteration:
        return None


def convert_tests_to_timeline(group: pd.DataFrame) -> pd.DataFrame:
    """
    Convert tests from the group into timeline table.

    Each row of the table consist of class name, method name, number of parametrized test, result,
    numbers of the first and the last consecutive submissions with this result.

    :param group: Group of submissions whose tests should be converted to a timeline table.
    :return: Timeline table.
    """
    unique_test_names = {
        (test.class_name, test.method_name, test.test_number)
        for tests in group[EduColumnName.TESTS.value]
        if tests is not None
        # We can't swap if and for because it could lead to iterating over None
        for test in tests  # noqa: WPS361
    }

    tests_timeline = []
    for class_name, method_name, test_number in unique_test_names:
        test_results = [
            None if attempt_tests is None else _find_test_result(class_name, method_name, test_number, attempt_tests)
            for attempt_tests in group[EduColumnName.TESTS.value]
        ]

        tests_timeline.extend(
            (class_name, method_name, test_number, result, start, finish)
            for result, start, finish in _convert_to_timeline(test_results)
            if result is not None
        )

    return pd.DataFrame(
        tests_timeline,
        columns=[
            TestDataField.CLASS_NAME.value,
            TestDataField.METHOD_NAME.value,
            TestDataField.TEST_NUMBER.value,
            TestDataField.RESULT.value,
            START_COLUMN,
            FINISH_COLUMN,
        ],
    )


def _get_aggregated_result(results: List[TestResult]) -> Optional[TestResult]:
    if not results:
        return None

    if any(result == TestResult.FAILED for result in results):
        return TestResult.FAILED

    if any(result == TestResult.IGNORED for result in results):
        return TestResult.IGNORED

    return TestResult.PASSED


def aggregate_tests_timeline(tests_timeline: pd.DataFrame) -> pd.DataFrame:
    """
    Convert parametrized tests into non-parametrized ones by aggregating their result.

    :param tests_timeline: Tests timeline with parametrized tests to aggregate.
    :return: Aggregated tests timeline.
    """
    non_parametrized_tests_timeline_mask = pd.isna(tests_timeline[TestDataField.TEST_NUMBER.value])
    non_parametrized_tests_timeline = tests_timeline[non_parametrized_tests_timeline_mask]
    parametrized_tests_timeline = tests_timeline[~non_parametrized_tests_timeline_mask]

    timeline_by_unique_parametrized_test_name = parametrized_tests_timeline.groupby(
        [TestDataField.CLASS_NAME.value, TestDataField.METHOD_NAME.value]
    )

    aggregated_tests_timeline_data = []
    for unique_test_name, test_timeline in timeline_by_unique_parametrized_test_name:
        aggregated_timeline = [None for _ in range(test_timeline[START_COLUMN].min() - 1)]
        for i in range(test_timeline[START_COLUMN].min(), test_timeline[FINISH_COLUMN].max() + 1):
            parametrized_test_results = []
            for row in test_timeline.itertuples():
                if getattr(row, START_COLUMN) <= i <= getattr(row, FINISH_COLUMN):
                    parametrized_test_results.append(getattr(row, TestDataField.RESULT.value))
            aggregated_timeline.append(_get_aggregated_result(parametrized_test_results))

        for result, begin, end in _convert_to_timeline(aggregated_timeline):
            if result is not None:
                aggregated_tests_timeline_data.append([*unique_test_name, None, result, begin, end])

    if not aggregated_tests_timeline_data:
        return non_parametrized_tests_timeline

    return pd.concat(
        [
            non_parametrized_tests_timeline,
            pd.DataFrame(aggregated_tests_timeline_data, columns=non_parametrized_tests_timeline.columns),
        ]
    ).reset_index(drop=True)


def pivot_tests(group: pd.DataFrame, aggregate: bool = True) -> pd.DataFrame:
    tests_timeline = convert_tests_to_timeline(group)
    if aggregate:
        tests_timeline = aggregate_tests_timeline(tests_timeline)

    exploded_tests_timeline = pd.DataFrame(
        [
            (
                getattr(row, TestDataField.CLASS_NAME.value),
                getattr(row, TestDataField.METHOD_NAME.value),
                getattr(row, TestDataField.TEST_NUMBER.value),
                getattr(row, TestDataField.RESULT.value),
                i,
            )
            for row in tests_timeline.itertuples()
            for i in range(getattr(row, START_COLUMN), getattr(row, FINISH_COLUMN) + 1)
        ],
        columns=[
            TestDataField.CLASS_NAME.value,
            TestDataField.METHOD_NAME.value,
            TestDataField.TEST_NUMBER.value,
            TestDataField.RESULT.value,
            'submission_number',
        ],
    )

    pivoted_tests = exploded_tests_timeline.pivot(
        index=[TestDataField.CLASS_NAME.value, TestDataField.METHOD_NAME.value, TestDataField.TEST_NUMBER.value],
        columns='submission_number',
        values=TestDataField.RESULT.value,
    )

    if pivoted_tests.columns.tolist() != list(range(1, len(group) + 1)):
        columns_to_add = set(range(1, len(group) + 1)) - set(pivoted_tests.columns.tolist())
        for column in columns_to_add:
            pivoted_tests[column] = None

        pivoted_tests = pivoted_tests.reindex(range(1, len(group) + 1), axis=1)

    if aggregate:
        pivoted_tests.index = pivoted_tests.index.droplevel(TestDataField.TEST_NUMBER.value)

    return pivoted_tests


def convert_test_results_to_numeral(df: pd.DataFrame) -> pd.DataFrame:
    return df.replace({TestResult.FAILED: 0, TestResult.PASSED: 1, None: 0}).convert_dtypes()


def convert_tests_to_chain(group: pd.DataFrame, aggregate: bool = True) -> pd.DataFrame:
    pivoted_tests = convert_test_results_to_numeral(pivot_tests(group, aggregate))
    return pivoted_tests.diff(axis=1).fillna(pivoted_tests)


TEST_NAME_DATA_COLUMN = 'test_name_data'
NUMBER_OF_ATTEMPTS_COLUMN = 'number_of_attempts'


def calculate_group_test_stats(group: pd.DataFrame, aggregate: bool) -> pd.DataFrame:
    pivoted_tests = pivot_tests(group, aggregate=aggregate)

    test_attempts = {}
    failed_test = set()

    # If we don't want to count the first attempts, then it should be equal to 0
    number_of_attempts = 1
    for i, column in pivoted_tests.items():
        passed_tests = pivoted_tests[column == TestResult.PASSED].index

        if i == 1:
            failed_test.update(pivoted_tests[column == TestResult.FAILED].index)

            for test in passed_tests:
                test_attempts[test] = 1

            number_of_attempts += 1

            continue

        solved_tests = failed_test.intersection(passed_tests)
        for test in solved_tests:
            test_attempts[test] = number_of_attempts

        if solved_tests:
            failed_test.difference_update(solved_tests)
            number_of_attempts = 1
        else:
            number_of_attempts += 1

    test_stats = pd.DataFrame.from_dict(test_attempts, columns=[NUMBER_OF_ATTEMPTS_COLUMN], orient='index')
    test_stats.index.name = TEST_NAME_DATA_COLUMN

    return test_stats
