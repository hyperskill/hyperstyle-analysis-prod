import json

import pandas as pd

from core.src.utils.df_utils import read_df
import streamlit as st

from jba.src.models.edu_columns import EduColumnName, EduTaskType
from jba.src.visualization.common.filters import (
    filter_by_task,
    filter_post_correct_submissions,
    filter_by_user,
    filter_by_group,
    filter_duplicate_submissions,
    filter_invalid_submissions,
)

from jba.src.visualization.common.widgets import select_file, select_view_type, show_code_viewer, show_group_info


def main():
    st.title('Submissions viewer')

    submissions = read_df(st.session_state.submissions_path)
    submissions[EduColumnName.CODE_SNIPPETS.value] = submissions[EduColumnName.CODE_SNIPPETS.value].apply(
        lambda code_snippets: code_snippets if pd.isna(code_snippets) else json.loads(code_snippets)
    )

    course_structure = read_df(st.session_state.course_structure_path)

    with st.sidebar:
        submissions = filter_post_correct_submissions(submissions)
        submissions = filter_invalid_submissions(submissions)
        submissions = filter_duplicate_submissions(submissions)

    columns = st.columns([1, 2, 1, 2, 1])

    with columns[0]:
        _, submissions = filter_by_user(submissions)

    with columns[1]:
        _, submissions = filter_by_task(submissions, course_structure, with_all_option=True)

    with columns[2]:
        _, submissions = filter_by_group(submissions)

    show_group_info(submissions)

    if submissions[EduColumnName.TASK_TYPE.value].iloc[0] == EduTaskType.THEORY.value:
        st.info("It's a theory group. Please choose another group.")
        st.stop()

    with columns[3]:
        file = select_file(submissions)

    with columns[4]:
        view_type = select_view_type(disabled=len(submissions) == 1)

    show_code_viewer(submissions, view_type, file)


if __name__ == '__main__':
    main()
