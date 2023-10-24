import streamlit as st

from core.src.utils.df_utils import read_df
from jba.src.plots.task_attempt import plot_task_attempts
from jba.src.plots.task_duplicates import plot_task_duplicates
from jba.src.plots.task_solving import plot_task_solving


def main():
    st.title('General stats')

    # TODO: check if session state has defined paths

    submissions = read_df(st.session_state.submissions_path)
    course_structure = read_df(st.session_state.course_structure_path)

    # TODO: add basic stats
    # TODO: do we really need a course structure in this visualization?
    #       Maybe we could use structure from submissions

    st.header('Task attempts')
    fig = plot_task_attempts(submissions, course_structure, st.session_state.course_name)
    st.pyplot(fig)

    st.header('Task solving')
    fig = plot_task_solving(submissions, course_structure, st.session_state.course_name)
    st.pyplot(fig)

    st.header('Task duplicates')
    fig = plot_task_duplicates(submissions, course_structure, st.session_state.course_name)
    st.pyplot(fig)


if __name__ == '__main__':
    main()
