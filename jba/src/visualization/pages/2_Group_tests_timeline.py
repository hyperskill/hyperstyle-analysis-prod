from typing import List

import pandas as pd
import streamlit as st

from core.src.utils.df_utils import read_df
from jba.src.models.edu_columns import EduColumnName, EduTaskType
from jba.src.models.edu_logs import TestDataField, TestResult
from jba.src.visualization.common import (
    filter_post_correct_submissions,
    filter_by_task,
    filter_by_group,
    filter_duplicate_submissions,
    filter_invalid_submissions,
)
from jba.src.test_logs.analysis import convert_tests_to_timeline, aggregate_tests_timeline, START_COLUMN, FINISH_COLUMN

import matplotlib.pyplot as plt
from matplotlib.patches import Patch

FAILED_COLOR = 'red'
IGNORED_COLOR = 'yellow'
PASSED_COLOR = 'green'
DUPLICATE_COLOR = '#d3d3d3'


def _get_result_color(result: TestResult) -> str:
    match result:
        case TestResult.FAILED:
            return FAILED_COLOR
        case TestResult.PASSED:
            return PASSED_COLOR
        case TestResult.IGNORED:
            return IGNORED_COLOR

    return 'black'


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


def main():
    st.title('Group tests timeline')

    submissions = read_df(st.session_state.submissions_path)
    course_structure = read_df(st.session_state.course_structure_path)

    # TODO: show visualizations for theory groups too (for example, quiz results)
    submissions = submissions[submissions.task_type != EduTaskType.THEORY.value].reset_index(drop=True)

    with st.sidebar:
        submissions = filter_post_correct_submissions(submissions)
        submissions = filter_invalid_submissions(submissions)
        submissions = filter_duplicate_submissions(submissions)

    left, right = st.columns([3, 1])

    with left:
        _, submissions = filter_by_task(submissions, course_structure)

    with right:
        _, submissions = filter_by_group(submissions)

    tests_timeline = convert_tests_to_timeline(submissions)

    duplicate_mask = (
        submissions[EduColumnName.CODE_SNIPPETS.value].shift()
        == submissions[EduColumnName.CODE_SNIPPETS.value]
    )
    duplicate_attempts = (duplicate_mask[duplicate_mask].index.values + 1).tolist()

    invalid_mask = pd.isna(submissions[EduColumnName.TESTS.value])
    invalid_attempts = (invalid_mask[invalid_mask].index.values + 1).tolist()

    st.subheader('Tests timeline')
    aggregated_tests_timeline = aggregate_tests_timeline(tests_timeline)
    plot_tests_timeline(aggregated_tests_timeline, duplicate_attempts, invalid_attempts)

    parametrized_tests_timeline = tests_timeline[~pd.isna(tests_timeline[TestDataField.TEST_NUMBER.value])]
    if not parametrized_tests_timeline.empty:
        st.subheader('Parametrized tests timeline')

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
