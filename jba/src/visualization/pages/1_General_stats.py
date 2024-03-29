import streamlit as st

from core.src.model.column_name import SubmissionColumns
from core.src.utils.df_utils import read_df
from jba.src.models.edu_columns import EduColumnName
from jba.src.plots.task_attempt import plot_task_attempts, calculate_attempt_stats
from jba.src.plots.task_duplicates import plot_task_duplicates
from jba.src.plots.task_solving import plot_task_solving, calculate_solving_stats
from jba.src.visualization.common.filters import filter_by_edu_columns
from jba.src.visualization.common.utils import ALL_CHOICE_OPTIONS, read_submissions
from jba.src.visualization.common.widgets import show_submission_postprocess_filters


def main():
    st.title('General stats')

    # TODO: check if session state has defined paths

    filters = show_submission_postprocess_filters()
    submissions = read_submissions(st.session_state.submissions_path, filters)
    course_structure = read_df(st.session_state.course_structure_path)

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
    attempt_stats = calculate_attempt_stats(submissions, course_structure)
    fig, _ = plot_task_attempts(attempt_stats)
    st.pyplot(fig)

    st.header('Task solving')
    solving_stats = calculate_solving_stats(submissions, course_structure)
    fig, _ = plot_task_solving(solving_stats)
    st.pyplot(fig)

    st.header('Task duplicates')
    fig = plot_task_duplicates(submissions, course_structure)
    st.pyplot(fig)


if __name__ == '__main__':
    main()
