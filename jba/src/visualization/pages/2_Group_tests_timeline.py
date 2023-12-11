import pandas as pd
import streamlit as st

from core.src.model.column_name import SubmissionColumns
from core.src.utils.df_utils import read_df
from jba.src.models.edu_columns import EduColumnName, EduTaskType
from jba.src.models.edu_logs import TestDataField
from jba.src.visualization.common import (
    convert_tests_to_timeline,
    aggregate_tests_timeline,
    plot_tests_timeline,
    show_exclude_post_correct_submissions_flag,
    show_filter_by_task,
)


def main():
    st.title('Group tests timeline')

    submissions = read_df(st.session_state.submissions_path)
    course_structure = read_df(st.session_state.course_structure_path)

    # TODO: show visualizations for theory groups too (for example, quiz results)
    submissions = submissions[submissions.task_type != EduTaskType.THEORY.value]

    with st.sidebar:
        submissions = show_exclude_post_correct_submissions_flag(submissions)

    left, right = st.columns([3, 1])

    with left:
        _, task_submissions = show_filter_by_task(submissions, course_structure)

    with right:
        group = st.selectbox('Group:', options=task_submissions[SubmissionColumns.GROUP.value].unique())

    group_submissions = task_submissions[task_submissions[SubmissionColumns.GROUP.value] == group].reset_index(
        drop=True
    )

    tests_timeline = convert_tests_to_timeline(group_submissions)

    duplicate_mask = (
        group_submissions[EduColumnName.CODE_SNIPPETS.value].shift()
        == group_submissions[EduColumnName.CODE_SNIPPETS.value]
    )
    duplicate_attempts = (duplicate_mask[duplicate_mask].index.values + 1).tolist()

    invalid_mask = pd.isna(group_submissions[EduColumnName.TESTS.value])
    invalid_attempts = (invalid_mask[invalid_mask].index.values + 1).tolist()

    st.subheader('Tests timeline')
    aggregated_tests_timeline = aggregate_tests_timeline(tests_timeline)
    plot_tests_timeline(aggregated_tests_timeline, duplicate_attempts, invalid_attempts)

    parametrized_tests_timeline = tests_timeline[~pd.isna(tests_timeline[TestDataField.TEST_NUMBER.value])]
    if not parametrized_tests_timeline.empty:
        st.subheader('Parametrized tests timeline')

        class_name, method_name = st.selectbox(
            'Parametrized test name:',
            options=(
                parametrized_tests_timeline[[TestDataField.CLASS_NAME.value, TestDataField.METHOD_NAME.value]]
                .drop_duplicates()
                .itertuples(index=False, name=None)
            ),
            format_func=lambda option: f'{option[0]}.{option[1]}',
        )

        parametrized_test_timeline = parametrized_tests_timeline[
            (parametrized_tests_timeline[TestDataField.CLASS_NAME.value] == class_name)
            & (parametrized_tests_timeline[TestDataField.METHOD_NAME.value] == method_name)
        ]

        plot_tests_timeline(parametrized_test_timeline, duplicate_attempts, invalid_attempts)


if __name__ == '__main__':
    main()
