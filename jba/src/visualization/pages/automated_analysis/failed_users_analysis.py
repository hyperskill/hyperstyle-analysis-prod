import pandas as pd
import streamlit as st

from core.src.model.column_name import SubmissionColumns
from jba.src.models.edu_columns import EduColumnName, EduTaskStatus
from jba.src.plots.task_solving import calculate_solving_stats, FAILED_COLUMN, TOTAL_COLUMN, plot_task_solving
from jba.src.visualization.pages.automated_analysis.common import (
    filter_submissions_and_show_code_viewer,
    convert_suspicious_tasks_to_markdown_list,
)


def show_failed_users_analysis(submissions: pd.DataFrame, course_structure: pd.DataFrame):
    st.header('Failed users analysis')

    stats = calculate_solving_stats(submissions, course_structure)

    threshold_column, _ = st.columns(2)

    with threshold_column, st.expander('Threshold:'):
        failed_threshold = st.number_input('Suspicious failed (%):', value=10, min_value=0, max_value=100)
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

    if suspicious_tasks.empty:
        st.write('There are no suspicious tasks! :dancer: :man_dancing:')
        st.stop()

    suspicious_tasks['percent'] = (suspicious_tasks[FAILED_COLUMN] / suspicious_tasks[TOTAL_COLUMN] * 100).round(2)
    suspicious_tasks.sort_values(by='percent', ascending=False, inplace=True)

    st.write(
        convert_suspicious_tasks_to_markdown_list(
            suspicious_tasks,
            lambda row: f'{row[FAILED_COLUMN]}/{row[TOTAL_COLUMN]} ({row["percent"]}%)',
        )
    )

    suspicious_submissions = (
        submissions[
            submissions[EduColumnName.TASK_GLOBAL_NUMBER.value].isin(
                suspicious_stats[EduColumnName.TASK_GLOBAL_NUMBER.value]
            )
        ]
        .groupby(SubmissionColumns.GROUP.value)
        .filter(lambda group: group[EduColumnName.STATUS.value].eq(EduTaskStatus.CORRECT.value).sum() == 0)
    )

    filter_submissions_and_show_code_viewer(suspicious_submissions, course_structure)
