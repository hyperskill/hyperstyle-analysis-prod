import pandas as pd
import streamlit as st

from core.src.model.column_name import SubmissionColumns
from jba.src.models.edu_columns import EduColumnName
from jba.src.plots.task_attempt import calculate_attempt_stats, MEDIAN_COLUMN, plot_task_attempts
from jba.src.visualization.pages.automated_analysis.common import (
    filter_submissions_and_show_code_viewer,
    convert_suspicious_tasks_to_markdown_list,
)


def show_median_attempts_analysis(submissions: pd.DataFrame, course_structure: pd.DataFrame):
    st.header('Task attempts analysis')

    stats = calculate_attempt_stats(submissions, course_structure)

    threshold_column, _ = st.columns(2)

    with threshold_column, st.expander('Threshold:'):
        median_threshold = st.number_input(
            'Suspicious median:',
            value=min(5.0, stats[MEDIAN_COLUMN].max()),
            min_value=stats[MEDIAN_COLUMN].min(),
            max_value=stats[MEDIAN_COLUMN].max(),
        )

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
    ).sort_values(by=MEDIAN_COLUMN, ascending=False)

    if suspicious_tasks.empty:
        st.write('There are no suspicious tasks! :dancer: :man_dancing:')
        st.stop()

    st.write(convert_suspicious_tasks_to_markdown_list(suspicious_tasks, lambda row: row[MEDIAN_COLUMN]))

    suspicious_submissions = (
        submissions[
            submissions[EduColumnName.TASK_GLOBAL_NUMBER.value].isin(
                suspicious_stats[EduColumnName.TASK_GLOBAL_NUMBER.value]
            )
        ]
        .groupby(SubmissionColumns.GROUP.value)
        .filter(lambda group: len(group) > median_threshold)
    )

    filter_submissions_and_show_code_viewer(suspicious_submissions, course_structure)
