import operator
from enum import Enum
from typing import Optional

import pandas as pd
import streamlit as st
from jba.src.inspections.analysis import find_code_snippet
from jba.src.models.edu_columns import EduColumnName, EduTaskStatus
from jba.src.models.edu_logs import ExceptionData, TestData, TestResult
from jba.src.visualization.common.utils import ALL_CHOICE_OPTIONS, get_edu_name_columns

from diff_viewer import diff_viewer


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

    raw_exceptions = submission[EduColumnName.EXCEPTIONS.value]
    if not pd.isna(raw_exceptions):
        exceptions = ExceptionData.schema().loads(raw_exceptions, many=True)
        if exceptions:
            with st.expander(f':red[Exception] {exceptions[0].message}'):
                st.json(ExceptionData.schema().dump(exceptions, many=True))

    raw_tests = submission[EduColumnName.TESTS.value]
    if not pd.isna(raw_tests):
        failed_tests = [
            test for test in TestData.schema().loads(raw_tests, many=True) if test.result == TestResult.FAILED
        ]
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
