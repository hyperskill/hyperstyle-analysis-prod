import streamlit as st

from core.src.model.column_name import SubmissionColumns
from core.src.utils.df_utils import read_df
from jba.src.models.edu_columns import EduColumnName
from jba.src.plots.task_attempt import plot_task_attempts
from jba.src.plots.task_duplicates import plot_task_duplicates
from jba.src.plots.task_solving import plot_task_solving
from jba.src.visualization.common import get_edu_name_columns

ALL_CHOICE_OPTIONS = 'All'


def main():
    st.title('General stats')

    # TODO: check if session state has defined paths

    submissions = read_df(st.session_state.submissions_path)
    course_structure = read_df(st.session_state.course_structure_path)

    edu_name_columns = get_edu_name_columns(submissions)
    show_stats_for = st.radio('Show stats for: ', options=edu_name_columns, horizontal=True)
    edu_name_columns = edu_name_columns[: edu_name_columns.index(show_stats_for) + 1]

    grouped_submissions = submissions.groupby(edu_name_columns)

    options = filter(
        lambda name: name in grouped_submissions.groups if len(name) > 1 else name[0] in grouped_submissions.groups,
        course_structure[edu_name_columns].drop_duplicates().itertuples(index=False, name=None),
    )

    selection = st.selectbox(
        f'{show_stats_for}:',
        options=[ALL_CHOICE_OPTIONS, *options],
        format_func=lambda option: option if option == ALL_CHOICE_OPTIONS else '/'.join(option),
    )

    selection = selection if len(selection) > 1 or selection == ALL_CHOICE_OPTIONS else selection[0]
    submissions = submissions if selection == ALL_CHOICE_OPTIONS else grouped_submissions.get_group(selection)

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
