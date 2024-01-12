import operator
from enum import Enum
from typing import Optional, List

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from diff_viewer import diff_viewer
from matplotlib.patches import Patch

from jba.src.inspections.analysis import find_code_snippet
from jba.src.models.edu_columns import EduColumnName, EduTaskStatus
from jba.src.models.edu_logs import ExceptionData, TestData, TestResult, TestDataField
from jba.src.test_logs.analysis import START_COLUMN, FINISH_COLUMN
from jba.src.visualization.common.utils import ALL_CHOICE_OPTIONS, get_edu_name_columns, PostprocessFilters


class ViewType(Enum):
    PER_SUBMISSION = 'Per submission'
    DIFFERENCE = 'Difference'


def select_view_type(disabled: bool = False) -> ViewType:
    return st.selectbox(
        'View type:',
        options=ViewType,
        format_func=lambda view_type: view_type.value,
        disabled=disabled,
    )


def select_file(submissions: pd.DataFrame, disabled: bool = False, with_all_option: bool = False) -> Optional[str]:
    options = (
        submissions[EduColumnName.CODE_SNIPPETS.value]
        .apply(lambda code_snippets: list(map(operator.itemgetter('name'), code_snippets)))
        .explode()
        .unique()
    )

    file = st.selectbox(
        'File:',
        options=[ALL_CHOICE_OPTIONS, *options] if with_all_option else options,
        disabled=disabled,
    )

    if file == ALL_CHOICE_OPTIONS:
        return None

    return file


def show_group_info(group: pd.DataFrame):
    st.markdown(
        f'**Task**: {"/".join(group[get_edu_name_columns(group)].iloc[0])}<br/>'
        f'**User**: {group[EduColumnName.USER_ID.value].iloc[0]}<br/>'
        f'**Number of submissions**: {len(group)}<br/>'
        f'**Has post-correct submissions**?: '
        f'{(group[EduColumnName.STATUS.value] == EduTaskStatus.CORRECT.value).sum() > 1}<br/>'
        f'**Is task solved?**: {EduTaskStatus.CORRECT.value in group[EduColumnName.STATUS.value].unique()}',
        unsafe_allow_html=True,
    )


def show_submission_info(submission: pd.Series):
    status = submission[EduColumnName.STATUS.value]
    if status == EduTaskStatus.CORRECT.value:
        color = 'green'
    else:
        color = 'red'

    st.write(f'Status: :{color}[{status.title()}]')

    exceptions = submission[EduColumnName.EXCEPTIONS.value]
    if exceptions:
        with st.expander(f':red[Exception] {exceptions[0].message}'):
            st.json(ExceptionData.schema().dump(exceptions, many=True))

    tests = submission[EduColumnName.TESTS.value]
    if tests:
        failed_tests = [test for test in tests if test.result == TestResult.FAILED]
        if failed_tests:
            with st.expander(f':violet[Failed test] {failed_tests[0].message}'):
                st.json(TestData.schema().dump(failed_tests, many=True))


def show_code_viewer(group: pd.DataFrame, view_type: ViewType, file: str):
    submission_number = 1
    if len(group) != 1:
        left, _ = st.columns([1, 6])

        with left:
            if view_type == ViewType.PER_SUBMISSION:
                submission_number = st.number_input('Submission number:', min_value=1, max_value=len(group))
            else:
                submission_number = st.number_input(
                    'Submissions diff pair number:',
                    min_value=1,
                    max_value=len(group) - 1,
                )

    if view_type == ViewType.PER_SUBMISSION or len(group) == 1:
        submission = group.iloc[submission_number - 1]

        show_submission_info(submission)

        st.code(
            find_code_snippet(submission[EduColumnName.CODE_SNIPPETS.value], file),
            language='kotlin',
            line_numbers=True,
        )
    else:
        submission_before = group.iloc[submission_number - 1]
        submission_after = group.iloc[submission_number]

        left, right = st.columns(2)

        with left:
            show_submission_info(submission_before)

        with right:
            show_submission_info(submission_after)

        diff_viewer(
            find_code_snippet(submission_before[EduColumnName.CODE_SNIPPETS.value], file),
            find_code_snippet(submission_after[EduColumnName.CODE_SNIPPETS.value], file),
            lang=None,
        )


def show_submission_postprocess_filters() -> PostprocessFilters:
    with st.sidebar:
        exclude_post_correct_submissions = st.checkbox(
            'Exclude post-correct submissions',
            value=False,
            help=(
                'If checked, then all submissions within one group '
                'that occur after the first correct submissions will be ignored.'
            ),
        )

        exclude_duplicate_submissions = st.checkbox('Exclude duplicate submissions', value=False)

        exclude_invalid_submissions = st.checkbox(
            'Exclude invalid submissions',
            value=False,
            help='If checked, then all submissions within one group, that have compilation exceptions will be ignored.',
        )

    return PostprocessFilters(
        exclude_post_correct_submissions,
        exclude_duplicate_submissions,
        exclude_invalid_submissions,
    )


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
