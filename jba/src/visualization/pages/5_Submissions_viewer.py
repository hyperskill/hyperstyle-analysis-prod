import json
import operator
from enum import Enum
from typing import List

import pandas as pd

from core.src.model.column_name import SubmissionColumns
from core.src.utils.df_utils import read_df
import streamlit as st

from jba.src.inspections.analysis import find_code_snippet
from jba.src.models.edu_columns import EduColumnName, EduTaskType, EduTaskStatus
from jba.src.models.edu_logs import TestData, TestResult, ExceptionData
from jba.src.visualization.common import get_edu_name_columns, show_filter_by_task, ALL_CHOICE_OPTIONS

from diff_viewer import diff_viewer


class ViewType(Enum):
    PER_SUBMISSION = 'Per submission'
    DIFFERENCE = 'Difference'

    @classmethod
    def values(cls) -> List[str]:
        return [view_type.value for view_type in cls]


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


def main():
    st.title('Submissions viewer')

    submissions = read_df(st.session_state.submissions_path)
    submissions[EduColumnName.CODE_SNIPPETS.value] = submissions[EduColumnName.CODE_SNIPPETS.value].apply(
        lambda code_snippets: code_snippets if pd.isna(code_snippets) else json.loads(code_snippets)
    )

    course_structure = read_df(st.session_state.course_structure_path)

    columns = st.columns([1, 2, 1, 2, 1])

    with columns[0]:
        user_id = st.text_input('User ID:')
        if user_id != '':
            submissions = submissions[submissions[SubmissionColumns.USER_ID.value] == user_id]

    with columns[1]:
        task, task_submissions = show_filter_by_task(submissions, course_structure, with_all_option=True)

    with columns[2]:
        if task == ALL_CHOICE_OPTIONS:
            group = st.number_input(
                'Group:',
                min_value=submissions[SubmissionColumns.GROUP.value].min(),
                max_value=submissions[SubmissionColumns.GROUP.value].max(),
            )
        else:
            group = st.selectbox('Group:', options=task_submissions[SubmissionColumns.GROUP.value].unique())

        group_submissions = submissions[submissions[SubmissionColumns.GROUP.value] == group].reset_index(drop=True)

    st.markdown(
        f'**Task**: {"/".join(group_submissions[get_edu_name_columns(group_submissions)].iloc[0])}<br/>'
        f'**User**: {group_submissions[EduColumnName.USER_ID.value].iloc[0]}<br/>'
        f'**Number of submissions**: {len(group_submissions)}<br/>'
        f'**Has post-correct submissions**?: '
        f'{(group_submissions[EduColumnName.STATUS.value] == EduTaskStatus.CORRECT.value).sum() > 1}<br/>'
        f'**Is task solved?**: {EduTaskStatus.CORRECT.value in group_submissions[EduColumnName.STATUS.value].unique()}',
        unsafe_allow_html=True,
    )

    if group_submissions[EduColumnName.TASK_TYPE.value].iloc[0] == EduTaskType.THEORY.value:
        st.info("It's a theory group. Please choose another group.")
        st.stop()

    with columns[3]:
        file = st.selectbox(
            'File:',
            options=map(operator.itemgetter('name'), group_submissions[EduColumnName.CODE_SNIPPETS.value].values[0]),
        )

    with columns[4]:
        view_type = ViewType(
            st.selectbox('View type:', options=ViewType.values(), disabled=len(group_submissions) == 1)
        )

    submission_number = 1
    if len(group_submissions) != 1:
        left, _ = st.columns([1, 3])

        with left:
            if view_type == ViewType.PER_SUBMISSION:
                submission_number = st.number_input('Submission number:', min_value=1, max_value=len(group_submissions))
            else:
                submission_number = st.number_input(
                    'Submissions diff pair number:',
                    min_value=1,
                    max_value=len(group_submissions) - 1,
                )

    if view_type == ViewType.PER_SUBMISSION or len(group_submissions) == 1:
        submission = group_submissions.iloc[submission_number - 1]

        show_submission_info(submission)

        st.code(
            find_code_snippet(submission[EduColumnName.CODE_SNIPPETS.value], file),
            language='kotlin',
            line_numbers=True,
        )
    else:
        submission_before = group_submissions.iloc[submission_number - 1]
        submission_after = group_submissions.iloc[submission_number]

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


if __name__ == '__main__':
    main()
