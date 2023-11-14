import json
import operator
from enum import Enum
from typing import List

import pandas as pd

from core.src.model.column_name import SubmissionColumns
from core.src.utils.df_utils import read_df
import streamlit as st

from jba.src.inspections.analysis import _find_code_snippet
from jba.src.models.edu_columns import EduColumnName, EduTaskType
from jba.src.visualization.common import get_edu_name_columns

from diff_viewer import diff_viewer


class ViewType(Enum):
    PER_SUBMISSION = 'Per submission'
    DIFFERENCE = 'Difference'

    @classmethod
    def values(cls) -> List[str]:
        return [view_type.value for view_type in cls]


def main():
    st.title('Submissions viewer')

    submissions = read_df(st.session_state.submissions_path)
    submissions[EduColumnName.CODE_SNIPPETS.value] = submissions[EduColumnName.CODE_SNIPPETS.value].apply(
        lambda code_snippets: code_snippets if pd.isna(code_snippets) else json.loads(code_snippets)
    )

    left, middle, right = st.columns([1, 2, 1])

    with left:
        group = st.number_input(
            'Group:',
            min_value=submissions[SubmissionColumns.GROUP.value].min(),
            max_value=submissions[SubmissionColumns.GROUP.value].max(),
        )

        group_submissions = submissions[submissions[SubmissionColumns.GROUP.value] == group].reset_index(drop=True)

    st.markdown(
        f'**Task**: {"/".join(group_submissions[get_edu_name_columns(group_submissions)].iloc[0])}<br/>'
        f'**User**: {group_submissions[EduColumnName.USER_ID.value].iloc[0]}<br/>'
        f'**Number of submissions**: {len(group_submissions)}',
        unsafe_allow_html=True,
    )

    if group_submissions[EduColumnName.TASK_TYPE.value].iloc[0] == EduTaskType.THEORY.value:
        st.info("It's a theory group. Please choose another group.")
        st.stop()

    with middle:
        file = st.selectbox(
            'File:',
            options=map(operator.itemgetter('name'), group_submissions[EduColumnName.CODE_SNIPPETS.value].values[0]),
        )

    with right:
        view_type = ViewType(st.selectbox('View type:', options=ViewType.values(), disabled=len(group_submissions) == 1))

    number = 1
    if len(group_submissions) != 1:
        left, _ = st.columns([1, 3])

        with left:
            if view_type == ViewType.PER_SUBMISSION:
                number = st.number_input('Submission number:', min_value=1, max_value=len(group_submissions))
            else:
                number = st.number_input(
                    'Submissions diff pair number:',
                    min_value=1,
                    max_value=len(group_submissions) - 1,
                )

    if view_type == ViewType.PER_SUBMISSION or len(group_submissions) == 1:
        st.code(
            _find_code_snippet(group_submissions[EduColumnName.CODE_SNIPPETS.value].iloc[number - 1], file),
            language='kotlin',
        )
    else:
        diff_viewer(
            _find_code_snippet(group_submissions[EduColumnName.CODE_SNIPPETS.value].iloc[number - 1], file),
            _find_code_snippet(group_submissions[EduColumnName.CODE_SNIPPETS.value].iloc[number], file),
            lang=None,
        )


if __name__ == '__main__':
    main()
