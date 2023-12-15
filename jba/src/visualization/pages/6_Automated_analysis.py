import json
from enum import Enum, unique

import pandas as pd
import streamlit as st

from core.src.model.column_name import SubmissionColumns
from core.src.utils.df_utils import read_df
from jba.src.models.edu_columns import EduColumnName, EduTaskStatus
from jba.src.plots.task_attempt import plot_task_attempts, calculate_attempt_stats, MEDIAN_COLUMN
from jba.src.plots.task_solving import calculate_solving_stats, FAILED_COLUMN, TOTAL_COLUMN, plot_task_solving
from jba.src.visualization.common.filters import (
    filter_by_task,
    filter_by_group,
    filter_post_correct_submissions,
    filter_invalid_submissions,
    filter_duplicate_submissions,
)
from jba.src.visualization.common.utils import get_edu_name_columns
from jba.src.visualization.common.widgets import select_file, select_view_type, show_code_viewer, show_group_info


@unique
class Analysis(Enum):
    BY_MEDIAN_ATTEMPTS = 'By median attempts'
    BY_FAILED_USERS = 'By failed users'

    def run(self, submissions: pd.DataFrame, course_structure: pd.DataFrame):
        analysis_to_main_function = {
            Analysis.BY_MEDIAN_ATTEMPTS: show_median_attempts_analysis,
            Analysis.BY_FAILED_USERS: show_failed_users_analysis,
        }

        return analysis_to_main_function[self](submissions, course_structure)


def _filter_submissions_and_show_code_viewer(submissions: pd.DataFrame, course_structure: pd.DataFrame) -> pd.DataFrame:
    columns = st.columns([2, 1, 2, 1])

    with columns[0]:
        _, submissions = filter_by_task(submissions, course_structure)
        group_info_placeholder = st.empty()

    with columns[1]:
        _, submissions = filter_by_group(submissions)
        with group_info_placeholder, st.expander('Group info'):
            show_group_info(submissions)

    with columns[2]:
        file = select_file(submissions)

    with columns[3]:
        view_type = select_view_type()

    show_code_viewer(submissions, view_type, file)


def show_median_attempts_analysis(submissions: pd.DataFrame, course_structure: pd.DataFrame):
    st.header('Task attempts analysis')

    stats = calculate_attempt_stats(submissions, course_structure)

    column, _ = st.columns(2)

    with column, st.expander('Threshold:'):
        median_threshold = st.number_input('Suspicious median:', value=5)

        suspicious_stats = stats[stats[MEDIAN_COLUMN] >= median_threshold]

        fig, ax = plot_task_attempts(stats)

        for tick_label in ax.xaxis.get_ticklabels():
            if tick_label.get_position()[0] not in suspicious_stats.index:
                tick_label.set_color('grey')

        st.pyplot(fig)

    st.subheader('Suspicious tasks')

    suspicious_tasks = suspicious_stats.merge(
        course_structure,
        on=[EduColumnName.TASK_GLOBAL_NUMBER.value, EduColumnName.TASK_NAME.value, EduColumnName.TASK_ID.value],
    )

    edu_name_columns = get_edu_name_columns(suspicious_tasks)

    st.write(suspicious_tasks[[*edu_name_columns, MEDIAN_COLUMN]])

    suspicious_submissions = (
        submissions[
            submissions[EduColumnName.TASK_GLOBAL_NUMBER.value].isin(
                suspicious_stats[EduColumnName.TASK_GLOBAL_NUMBER.value]
            )
        ]
        .groupby(SubmissionColumns.GROUP.value)
        .filter(lambda group: len(group) > median_threshold)
    )

    _filter_submissions_and_show_code_viewer(suspicious_submissions, course_structure)


def show_failed_users_analysis(submissions: pd.DataFrame, course_structure: pd.DataFrame):
    st.header('Failed users analysis')

    stats = calculate_solving_stats(submissions, course_structure)

    column, _ = st.columns(2)

    with column, st.expander('Threshold:'):
        failed_threshold = st.number_input('Suspicious failed (%):', value=10)

        suspicious_stats = stats[stats[FAILED_COLUMN] / stats[TOTAL_COLUMN] * 100 >= failed_threshold]

        fig, ax = plot_task_solving(stats)

        for tick_label in ax.xaxis.get_ticklabels():
            if tick_label.get_position()[0] not in suspicious_stats.index:
                tick_label.set_color('grey')

        st.pyplot(fig)

    st.subheader('Suspicious tasks')

    suspicious_tasks = suspicious_stats.merge(
        course_structure,
        on=[EduColumnName.TASK_GLOBAL_NUMBER.value, EduColumnName.TASK_NAME.value, EduColumnName.TASK_ID.value],
    )

    suspicious_tasks['percent'] = (suspicious_tasks[FAILED_COLUMN] / suspicious_tasks[TOTAL_COLUMN] * 100).round(2)

    edu_name_columns = get_edu_name_columns(suspicious_tasks)

    st.write(suspicious_tasks[[*edu_name_columns, FAILED_COLUMN, TOTAL_COLUMN, 'percent']])

    suspicious_submissions = (
        submissions[
            submissions[EduColumnName.TASK_GLOBAL_NUMBER.value].isin(
                suspicious_stats[EduColumnName.TASK_GLOBAL_NUMBER.value]
            )
        ]
        .groupby(SubmissionColumns.GROUP.value)
        .filter(lambda group: group[EduColumnName.STATUS.value].eq(EduTaskStatus.CORRECT.value).sum() == 0)
    )

    _filter_submissions_and_show_code_viewer(suspicious_submissions, course_structure)


def main():
    with st.sidebar:
        analysis = st.selectbox('Analysis:', options=Analysis, format_func=lambda item: item.value)

    submissions = read_df(st.session_state.submissions_path)
    course_structure = read_df(st.session_state.course_structure_path)

    submissions[EduColumnName.CODE_SNIPPETS.value] = submissions[EduColumnName.CODE_SNIPPETS.value].apply(
        lambda code_snippets: code_snippets if pd.isna(code_snippets) else json.loads(code_snippets)
    )

    with st.sidebar:
        submissions = filter_post_correct_submissions(submissions)
        submissions = filter_invalid_submissions(submissions)
        submissions = filter_duplicate_submissions(submissions)

    analysis.run(submissions, course_structure)


if __name__ == '__main__':
    main()
