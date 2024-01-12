import pandas as pd
import streamlit as st

from core.src.utils.df_utils import read_df
from jba.src.models.edu_columns import EduColumnName, EduTaskType
from jba.src.models.edu_logs import TestDataField
from jba.src.test_logs.analysis import convert_tests_to_timeline, aggregate_tests_timeline
from jba.src.visualization.common.filters import filter_by_task, filter_by_group
from jba.src.visualization.common.utils import (
    read_submissions,
    fix_submissions_after_filtering,
    find_duplicate_attempts,
    find_invalid_attempts,
)
from jba.src.visualization.common.widgets import show_submission_postprocess_filters, plot_tests_timeline


def main():
    st.title('Group tests timeline')

    filters = show_submission_postprocess_filters()
    submissions = read_submissions(st.session_state.submissions_path, filters)
    course_structure = read_df(st.session_state.course_structure_path)

    # TODO: show visualizations for theory groups too (for example, quiz results)
    submissions = submissions[submissions[EduColumnName.TASK_TYPE.value] != EduTaskType.THEORY.value]
    submissions = fix_submissions_after_filtering(submissions)

    left, right = st.columns([3, 1])

    with left:
        _, submissions = filter_by_task(submissions, course_structure)

    with right:
        _, submissions = filter_by_group(submissions)

    tests_timeline = convert_tests_to_timeline(submissions)
    duplicate_attempts = find_duplicate_attempts(submissions)
    invalid_attempts = find_invalid_attempts(submissions)

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
