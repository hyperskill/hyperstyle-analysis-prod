import itertools
from typing import TypeVar, Tuple, Sequence, List, Optional

import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt
from matplotlib.patches import Patch

from jba.src.models.edu_columns import EduColumnName
from jba.src.models.edu_logs import TestDataField, TestData, TestResult

START_COLUMN = 'start'
FINISH_COLUMN = 'finish'

FAILED_COLOR = 'red'
IGNORED_COLOR = 'yellow'
PASSED_COLOR = 'green'
DUPLICATE_COLOR = '#d3d3d3'

T = TypeVar('T')

# element, start, finish
TimelineItem = Tuple[T, int, int]


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


def _get_result_color(result: TestResult) -> str:
    match result:
        case TestResult.FAILED:
            return FAILED_COLOR
        case TestResult.PASSED:
            return PASSED_COLOR
        case TestResult.IGNORED:
            return IGNORED_COLOR

    return 'black'


def convert_tests_to_timeline(group: pd.DataFrame) -> pd.DataFrame:
    """
    Convert tests from the group into timeline table.

    Each row of the table consist of class name, method name, number of parametrized test, result,
    numbers of the first and the last consecutive submissions with this result.

    :param group: Group of submissions whose tests should be converted to a timeline table.
    :return: Timeline table.
    """
    group_tests = group[EduColumnName.TESTS.value].apply(
        lambda tests: None if pd.isna(tests) else TestData.schema().loads(tests, many=True)
    )

    unique_test_names = {
        (test.class_name, test.method_name, test.test_number)
        for tests in group_tests
        if tests is not None
        # We can't swap if and for because it could lead to iterating over None
        for test in tests  # noqa: WPS361
    }

    tests_timeline = []
    for class_name, method_name, test_number in unique_test_names:
        test_results = [
            None if attempt_tests is None else _find_test_result(class_name, method_name, test_number, attempt_tests)
            for attempt_tests in group_tests
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


def plot_tests_timeline(tests_timeline: pd.DataFrame, duplicate_attempts: List[int], invalid_attempts: List[int]):
    """
    Plot tests timeline.

    :param tests_timeline: Tests timeline.
    :param duplicate_attempts: Numbers of submissions with duplicate attempts.
    :param invalid_attempts: Numbers of submissions with invalid attempts.
    """
    timeline_by_unique_test_name = tests_timeline.groupby(
        [TestDataField.CLASS_NAME.value, TestDataField.METHOD_NAME.value, TestDataField.TEST_NUMBER.value],
        dropna=False,
    )

    fig, ax = plt.subplots()

    yticks = []
    yticklabels = []
    for i, (unique_test_name, test_timeline) in enumerate(timeline_by_unique_test_name, start=1):
        class_name, method_name, test_number = unique_test_name

        xranges = []
        colors = []
        for row in test_timeline.itertuples():
            start = getattr(row, START_COLUMN)
            finish = getattr(row, FINISH_COLUMN)
            duration = finish - start
            color = _get_result_color(getattr(row, TestDataField.RESULT.value))

            if duration == 0:
                plt.plot(start, i + 0.25, marker='o', markerfacecolor=color, markeredgecolor=color, markersize=5)
            else:
                xranges.append((start, duration))
                colors.append(color)

        test_name = f'{class_name}.{method_name}'
        if not pd.isna(test_number):
            # We use explicit string concatenation here for the sake of brevity
            test_name += f'[{int(test_number)}]'  # noqa: WPS336

        yticks.append(i + 0.25)
        yticklabels.append(test_name)

        plt.broken_barh(xranges=xranges, yrange=(i, 0.5), facecolors=colors)

    ax.set_yticks(yticks)
    ax.set_yticklabels(yticklabels)
    ax.invert_yaxis()

    ax.set_xlabel('Attempt')

    ax.legend(
        handles=[
            Patch(facecolor=FAILED_COLOR, label='Failed'),
            Patch(facecolor=IGNORED_COLOR, label='Ignored'),
            Patch(facecolor=PASSED_COLOR, label='Passed'),
            Patch(facecolor=DUPLICATE_COLOR, label='Duplicate'),
        ],
        bbox_to_anchor=(1.02, 1),
        borderaxespad=0,
        loc='upper left',
    )

    left_boundary = min([tests_timeline[START_COLUMN].min(), *invalid_attempts])
    right_boundary = max([tests_timeline[FINISH_COLUMN].max(), *invalid_attempts])
    ax.set_xticks(range(left_boundary, right_boundary + 1))

    for attempt in duplicate_attempts:
        ax.get_xticklabels()[attempt - 1].set_color(DUPLICATE_COLOR)

    st.pyplot(fig)
