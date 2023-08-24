# TODO: docs
# TODO: tests everywhere
# TODO: add caching
# TODO: add legend
import itertools
from typing import List, Tuple, Optional, TypeVar, Sequence

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from matplotlib.patches import Patch

from core.src.model.column_name import SubmissionColumns
from core.src.utils.df_utils import read_df
from jba.src.models.edu_columns import EduColumnName, EduTaskType
from jba.src.models.edu_logs import TestData, TestDataField, TestResult

START_COLUMN = 'start'
FINISH_COLUMN = 'finish'

LIGHT_GRAY_COLOR = '#d3d3d3'

T = TypeVar('T')

# element, start, finish
TimelineItem = Tuple[T, int, int]


def _convert_to_timeline(elements: Sequence[T]) -> List[TimelineItem]:
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
    test_number: int,
    tests: List[TestData],
) -> Optional[TestResult]:
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
            return "red"
        case TestResult.PASSED:
            return "green"
        case TestResult.IGNORED:
            return "yellow"
        case _:
            return "black"


@st.cache_data
def convert_tests_to_timeline(group: pd.DataFrame) -> pd.DataFrame:
    group_tests = group[EduColumnName.TESTS.value].apply(
        lambda tests: None if pd.isna(tests) else TestData.schema().loads(tests, many=True)
    )

    unique_test_names = {
        (test.class_name, test.method_name, test.test_number)
        for tests in group_tests
        if tests is not None
        for test in tests
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
    non_parametrized_tests_timeline_mask = pd.isna(tests_timeline[TestDataField.TEST_NUMBER.value])
    non_parametrized_tests_timeline = tests_timeline[non_parametrized_tests_timeline_mask]
    parametrized_tests_timeline = tests_timeline[~non_parametrized_tests_timeline_mask]

    aggregated_tests_timeline_data = []
    for unique_test_name, group in parametrized_tests_timeline.groupby(
        [TestDataField.CLASS_NAME.value, TestDataField.METHOD_NAME.value]
    ):
        aggregated_timeline = [None for _ in range(group[START_COLUMN].min() - 1)]
        for i in range(group[START_COLUMN].min(), group[FINISH_COLUMN].max() + 1):
            parametrized_test_results = []
            for row in group.itertuples():
                if getattr(row, START_COLUMN) <= i <= getattr(row, FINISH_COLUMN):
                    parametrized_test_results.append(getattr(row, TestDataField.RESULT.value))
            aggregated_timeline.append(_get_aggregated_result(parametrized_test_results))

        for result, begin, end in _convert_to_timeline(aggregated_timeline):
            if result is not None:
                aggregated_tests_timeline_data.append([*unique_test_name, None, result, begin, end])

    return pd.concat(
        [
            non_parametrized_tests_timeline,
            pd.DataFrame(aggregated_tests_timeline_data, columns=non_parametrized_tests_timeline.columns),
        ]
    )


# TODO: make bars slimmer
def plot_tests_timeline(tests_timeline: pd.DataFrame, duplicate_attempts: List[int], invalid_attempts: List[int]):
    timeline_by_unique_test_name = tests_timeline.groupby(
        [TestDataField.CLASS_NAME.value, TestDataField.METHOD_NAME.value, TestDataField.TEST_NUMBER.value],
        dropna=False,
    )

    fig, ax = plt.subplots()

    yticks = []
    yticklabels = []
    for i, (unique_test_name, tests_timeline) in enumerate(timeline_by_unique_test_name, start=1):
        class_name, method_name, test_number = unique_test_name

        xranges = []
        colors = []
        for row in tests_timeline.itertuples():
            start = getattr(row, START_COLUMN)
            finish = getattr(row, FINISH_COLUMN)
            duration = finish - start
            color = _get_result_color(getattr(row, TestDataField.RESULT.value))

            if duration != 0:
                xranges.append((start, duration))
                colors.append(color)
            else:
                plt.plot(start, i + 0.25, marker='o', markerfacecolor=color, markeredgecolor=color, markersize=5)

        test_name = f'{class_name}.{method_name}'
        if not pd.isna(test_number):
            test_name += f'[{int(test_number)}]'

        yticks.append(i + 0.25)
        yticklabels.append(test_name)

        plt.broken_barh(xranges=xranges, yrange=(i, 0.5), facecolors=colors)

    ax.set_yticks(yticks)
    ax.set_yticklabels(yticklabels)
    ax.invert_yaxis()

    ax.legend(
        handles=[
            Patch(facecolor='red', label='Failed'),
            Patch(facecolor='yellow', label='Ignored'),
            Patch(facecolor='green', label='Passed'),
            Patch(facecolor=LIGHT_GRAY_COLOR, label='Duplicate'),
        ],
        bbox_to_anchor=(1.02, 1),
        borderaxespad=0.0,
        loc='upper left',
    )

    # TODO: ?????
    left_boundary = min(tests_timeline[START_COLUMN].min(), tests_timeline[START_COLUMN].min(), *invalid_attempts)
    right_boundary = max(tests_timeline[FINISH_COLUMN].max(), tests_timeline[FINISH_COLUMN].max(), *invalid_attempts)
    ax.set_xticks(range(left_boundary, right_boundary + 1))

    for attempt in duplicate_attempts:
        ax.get_xticklabels()[attempt - 1].set_color(LIGHT_GRAY_COLOR)

    st.pyplot(fig)


def main():
    st.title('Tests Analysis')

    submissions_path = st.text_input('Submissions path:')
    if not submissions_path:
        st.info('You should enter the submissions path.')
        st.stop()

    submissions = read_df(submissions_path)

    group = st.number_input(
        'Group:',
        value=submissions[SubmissionColumns.GROUP.value].min(),
        min_value=submissions[SubmissionColumns.GROUP.value].min(),
        max_value=submissions[SubmissionColumns.GROUP.value].max(),
    )

    group_submissions = submissions[submissions[SubmissionColumns.GROUP.value] == group].reset_index(drop=True)

    if group_submissions[EduColumnName.TASK_TYPE.value].iloc[0] == EduTaskType.THEORY.value:
        st.info("It's a theory group. Please choose another group.")
        st.stop()

    tests_timeline = convert_tests_to_timeline(group_submissions)

    duplicate_mask = (
        group_submissions[EduColumnName.CODE_SNIPPETS.value].shift()
        == group_submissions[EduColumnName.CODE_SNIPPETS.value]
    )
    duplicate_attempts = (duplicate_mask[duplicate_mask].index.values + 1).tolist()

    invalid_mask = pd.isna(group_submissions[EduColumnName.TESTS.value])
    invalid_attempts = (invalid_mask[invalid_mask].index.values + 1).tolist()

    aggregated_tests_timeline = aggregate_tests_timeline(tests_timeline)
    plot_tests_timeline(aggregated_tests_timeline, duplicate_attempts, invalid_attempts)

    parametrized_tests_timeline = tests_timeline[~pd.isna(tests_timeline[TestDataField.TEST_NUMBER.value])]
    if len(parametrized_tests_timeline) != 0:
        class_name, method_name = st.selectbox(
            'Parametrized test name:',
            options=(
                parametrized_tests_timeline[[TestDataField.CLASS_NAME.value, TestDataField.METHOD_NAME.value]]
                .drop_duplicates()
                .itertuples(index=False, name=None)
            ),
            format_func=lambda option: f'{option[0]}.{option[1]}',
        )

        parametrized_test_timeline = parametrized_tests_timeline[
            (parametrized_tests_timeline[TestDataField.CLASS_NAME.value] == class_name)
            & (parametrized_tests_timeline[TestDataField.METHOD_NAME.value] == method_name)
        ]

        plot_tests_timeline(parametrized_test_timeline, duplicate_attempts, invalid_attempts)


if __name__ == '__main__':
    main()
