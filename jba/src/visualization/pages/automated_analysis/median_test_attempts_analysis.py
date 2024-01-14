from typing import List

import pandas as pd
import streamlit as st

from core.src.model.column_name import SubmissionColumns
from jba.src.models.edu_columns import EduTaskType, EduColumnName
from jba.src.models.edu_logs import TestDataField
from jba.src.test_logs.analysis import (
    calculate_group_test_stats,
    convert_tests_to_timeline,
    aggregate_tests_timeline,
    NUMBER_OF_ATTEMPTS_COLUMN,
    TEST_NAME_DATA_COLUMN,
)
from jba.src.visualization.common.filters import filter_by_group, filter_by_task
from jba.src.visualization.common.utils import (
    get_edu_name_columns,
    fix_submissions_after_filtering,
    find_duplicate_attempts,
    find_invalid_attempts,
)
from jba.src.visualization.common.widgets import (
    show_group_info,
    select_file,
    select_view_type,
    show_code_viewer,
    plot_tests_timeline,
)


@st.cache_data(show_spinner='Looking for suspicious tests... :eyes:')
def calculate_test_stats(submissions: pd.DataFrame) -> pd.DataFrame:
    edu_name_columns = get_edu_name_columns(submissions)

    return (
        submissions.groupby([*edu_name_columns, SubmissionColumns.GROUP.value])
        .apply(calculate_group_test_stats, aggregate=True)
        .reset_index()
    )


def _convert_suspicious_tests_to_markdown_list(suspicious_tests: pd.DataFrame, edu_name_columns: List[str]) -> str:
    data = suspicious_tests[[*edu_name_columns, TEST_NAME_DATA_COLUMN, NUMBER_OF_ATTEMPTS_COLUMN]]

    data['task_fq_name'] = data[edu_name_columns].apply(lambda element: "/".join(element), axis=1)
    data['test_fq_name'] = data[TEST_NAME_DATA_COLUMN].apply(lambda element: ".".join(element))

    data['test_stat_item'] = data.apply(
        lambda row: f'\t* {row["test_fq_name"]} – {row[NUMBER_OF_ATTEMPTS_COLUMN]}',
        axis=1,
    )

    return '\n'.join(
        data.groupby('task_fq_name').apply(lambda group: '\n'.join([f'* {group.name}:', *group['test_stat_item']]))
    )


def show_test_attempts_analysis(submissions: pd.DataFrame, course_structure: pd.DataFrame) -> pd.DataFrame:
    st.header('Test attempts analysis')

    submissions = submissions[submissions[EduColumnName.TASK_TYPE.value] != EduTaskType.THEORY.value]

    submissions = submissions.groupby(SubmissionColumns.GROUP.value, as_index=False).apply(
        lambda group: group.loc[~pd.isna(group[EduColumnName.TESTS.value])]
    )

    submissions = fix_submissions_after_filtering(submissions)
    edu_name_columns = get_edu_name_columns(submissions)

    test_stats = calculate_test_stats(submissions)

    test_stats_median = test_stats.groupby(by=[*edu_name_columns, TEST_NAME_DATA_COLUMN], as_index=False).agg(
        {NUMBER_OF_ATTEMPTS_COLUMN: 'median'}
    )

    median_input_column, _ = st.columns([2, 6])
    with median_input_column:
        suspicious_median = st.number_input(
            'Suspicious median:',
            value=min(3.0, test_stats_median[NUMBER_OF_ATTEMPTS_COLUMN].max()),
            min_value=test_stats_median[NUMBER_OF_ATTEMPTS_COLUMN].min(),
            max_value=test_stats_median[NUMBER_OF_ATTEMPTS_COLUMN].max(),
        )

    st.subheader('Suspicious tests')

    suspicious_tests = test_stats_median[test_stats_median[NUMBER_OF_ATTEMPTS_COLUMN] >= suspicious_median]

    if suspicious_tests.empty:
        st.write('There are no suspicious tests! :dancer: :man_dancing:')
        st.stop()

    st.markdown(_convert_suspicious_tests_to_markdown_list(suspicious_tests, edu_name_columns))

    filter_columns = st.columns([2, 2, 1, 2, 1])

    with filter_columns[0]:
        task, suspicious_tests = filter_by_task(suspicious_tests, course_structure)

    with filter_columns[1]:
        test = st.selectbox(
            'Test:',
            options=suspicious_tests[TEST_NAME_DATA_COLUMN],
            format_func=lambda value: '.'.join(value),
        )

        suspicious_tests = suspicious_tests[suspicious_tests[TEST_NAME_DATA_COLUMN] == test]

    suspicious_test_stats = pd.merge(test_stats, suspicious_tests[[*edu_name_columns, TEST_NAME_DATA_COLUMN]])
    suspicious_test_stats = suspicious_test_stats[suspicious_test_stats[NUMBER_OF_ATTEMPTS_COLUMN] >= suspicious_median]

    suspicious_submissions = submissions[
        submissions[SubmissionColumns.GROUP.value].isin(suspicious_test_stats[SubmissionColumns.GROUP.value])
    ].reset_index(drop=True)

    with filter_columns[2]:
        _, suspicious_submissions = filter_by_group(suspicious_submissions)

    with filter_columns[3]:
        file = select_file(suspicious_submissions)

    with filter_columns[4]:
        view_type = select_view_type()

    group_column, aggregated_timeline_column, parametrized_timeline_column = st.columns([2, 3, 3])

    with group_column, st.expander('Group info'):
        show_group_info(suspicious_submissions)

    tests_timeline = convert_tests_to_timeline(suspicious_submissions)
    duplicate_attempts = find_duplicate_attempts(suspicious_submissions)
    invalid_attempts = find_invalid_attempts(suspicious_submissions)

    with aggregated_timeline_column, st.expander('Aggregated test timeline'):
        aggregated_tests_timeline = aggregate_tests_timeline(tests_timeline)
        plot_tests_timeline(aggregated_tests_timeline, duplicate_attempts, invalid_attempts)

    parametrized_tests_timeline = tests_timeline[~pd.isna(tests_timeline[TestDataField.TEST_NUMBER.value])]
    if not parametrized_tests_timeline.empty:
        with parametrized_timeline_column, st.expander('Parametrized test timeline'):
            parametrized_test_timeline = parametrized_tests_timeline.groupby(
                by=[TestDataField.CLASS_NAME.value, TestDataField.METHOD_NAME.value],
            ).get_group(test)

            plot_tests_timeline(parametrized_test_timeline, duplicate_attempts, invalid_attempts)

    show_code_viewer(suspicious_submissions, view_type, file)
