import streamlit as st

from core.src.model.column_name import SubmissionColumns
from core.src.utils.df_utils import read_df
from jba.src.models.edu_columns import EduColumnName
from jba.src.plots.task_attempt import plot_task_attempts
from jba.src.plots.task_duplicates import plot_task_duplicates
from jba.src.plots.task_solving import plot_task_solving
from jba.src.visualization.common import (
    filter_post_correct_submissions,
    filter_duplicate_submissions,
    filter_invalid_submissions,
    filter_by_edu_columns,
    ALL_CHOICE_OPTIONS,
)


def main():
    st.title('General stats')

    # TODO: check if session state has defined paths

    submissions = read_df(st.session_state.submissions_path)
    course_structure = read_df(st.session_state.course_structure_path)

    with st.sidebar:
        submissions = filter_post_correct_submissions(submissions)
        submissions = filter_invalid_submissions(submissions)
        submissions = filter_duplicate_submissions(submissions)

    show_stats_for, selection, submissions = filter_by_edu_columns(course_structure, submissions)

    st.header('Basic stats')

    left, middle, right = st.columns(3)
    with left:
        st.metric('Number of submissions:', len(submissions))

    with middle:
        st.metric('Number of users:', submissions[EduColumnName.USER_ID.value].nunique())

    with right:
        st.metric('Number of solution groups:', submissions[SubmissionColumns.GROUP.value].nunique())

    if show_stats_for == EduColumnName.TASK_NAME.value and selection != ALL_CHOICE_OPTIONS:
        st.stop()

    st.header('Task attempts')
    fig = plot_task_attempts(submissions, course_structure)
    st.pyplot(fig)

    st.header('Task solving')
    fig = plot_task_solving(submissions, course_structure)
    st.pyplot(fig)

    st.header('Task duplicates')
    fig = plot_task_duplicates(submissions, course_structure)
    st.pyplot(fig)


if __name__ == '__main__':
    main()
