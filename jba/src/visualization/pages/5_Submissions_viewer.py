import streamlit as st

from core.src.utils.df_utils import read_df
from jba.src.models.edu_columns import EduColumnName, EduTaskType
from jba.src.visualization.common.filters import filter_by_task, filter_by_user, filter_by_group
from jba.src.visualization.common.utils import read_submissions, fix_submissions_after_filtering
from jba.src.visualization.common.widgets import (
    select_file,
    select_view_type,
    show_code_viewer,
    show_group_info,
    show_submission_postprocess_filters,
)


def main():
    st.title('Submissions viewer')

    filters = show_submission_postprocess_filters()
    submissions = read_submissions(st.session_state.submissions_path, filters)
    course_structure = read_df(st.session_state.course_structure_path)

    submissions = submissions[submissions[EduColumnName.TASK_TYPE.value] != EduTaskType.THEORY.value]
    submissions = fix_submissions_after_filtering(submissions)

    columns = st.columns([1, 2, 1, 2, 1])

    with columns[0]:
        _, submissions = filter_by_user(submissions)

    with columns[1]:
        _, submissions = filter_by_task(submissions, course_structure, with_all_option=True)

    with columns[2]:
        _, submissions = filter_by_group(submissions)

    show_group_info(submissions)

    with columns[3]:
        file = select_file(submissions)

    with columns[4]:
        view_type = select_view_type(disabled=len(submissions) == 1)

    show_code_viewer(submissions, view_type, file)


if __name__ == '__main__':
    main()
