from typing import List, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from core.src.model.column_name import SubmissionColumns
from core.src.utils.df_utils import read_df
from jba.src.models.edu_columns import EduColumnName
from jba.src.models.edu_logs import TestData, TestDataField


def accumulate_results(results: List[str]) -> List[Tuple[str, int, int]]:
    res = []

    prev_result = None
    start = None
    end = None
    for result in results:
        if prev_result is None:
            prev_result = result
            start = 1
            end = 1
            continue

        if prev_result == result:
            end += 1
        else:
            res.append((prev_result, start, end))
            start = end + 1
            end = start
            prev_result = result

    if start <= len(results):
        res.append((prev_result, start, end))

    return res


def get_aggregated_status(statuses: List[str]):
    if any(status == 'failed' for status in statuses):
        return 'failed'
    return 'passed'


def get_result(class_name: str, method_name: str, test_number: int, tests: List[TestData]) -> str:
    # TODO
    try:
        return next(
            (
                test
                for test in tests
                if test.class_name == class_name and test.method_name == method_name and test.test_number == test_number
            )
        ).result
    except:
        return None


def convert_parametrized_tests_to_timeline(group: pd.DataFrame) -> pd.DataFrame:
    # TODO: naming
    group_tests = [
        TestData.schema().loads(getattr(row, EduColumnName.TESTS.value), many=True) for row in group.itertuples()
    ]
    unique_names = {(test.class_name, test.method_name, test.test_number) for tests in group_tests for test in tests}

    res = []
    for class_name, method_name, test_number in unique_names:
        # TODO: what if there is no equal elements in the first list
        result = get_result(class_name, method_name, test_number, group_tests[0])
        if result is None:
            return None
        begin = 1
        end = 1

        # TODO: enumerate
        for attempt_tests in group_tests[1:]:
            current_result = get_result(class_name, method_name, test_number, attempt_tests)

            if current_result == result:
                end += 1
            else:
                res.append((class_name, method_name, test_number, result, begin, end))
                begin = end + 1
                end = begin
                result = current_result

        if begin <= len(group_tests):
            res.append((class_name, method_name, test_number, result, begin, end))

    return pd.DataFrame(
        res,
        columns=[
            TestDataField.CLASS_NAME.value,
            TestDataField.METHOD_NAME.value,
            TestDataField.TEST_NUMBER.value,
            TestDataField.RESULT.value,
            'begin',
            'end',
        ],
    )


def plot_general(timeline: pd.DataFrame, duplicate_attempts):
    general_tests_timeline = timeline[pd.isna(timeline[TestDataField.TEST_NUMBER.value])]
    parametrized_tests_timeline = timeline[~pd.isna(timeline[TestDataField.TEST_NUMBER.value])]

    for name, group in parametrized_tests_timeline.groupby(['class_name', 'method_name']):
        result_timeline = []
        for i in range(group['begin'].min(), group['end'].max() + 1):
            statuses = []
            for row in group.itertuples():
                if getattr(row, 'begin') <= i <= getattr(row, 'end'):
                    statuses.append(getattr(row, 'result'))
            result_timeline.append(get_aggregated_status(statuses))

        for status, begin, end in accumulate_results(result_timeline):
            general_tests_timeline.loc[general_tests_timeline.index.max() + 1] = [*name, None, status, begin, end]

    plot(general_tests_timeline, duplicate_attempts)


def plot(timeline: pd.DataFrame, duplicate_attempts: List[int]):
    plt.figure(dpi=300)
    fig, ax = plt.subplots()

    i = 1
    yticks = []
    yticklabels = []
    for (class_name, method_name, test_number), group in timeline.groupby(
        [TestDataField.CLASS_NAME.value, TestDataField.METHOD_NAME.value, TestDataField.TEST_NUMBER.value],
        dropna=False,
    ):
        xranges = []
        colors = []

        for row in group.itertuples():
            begin = getattr(row, 'begin')
            end = getattr(row, 'end')
            dur = end - begin
            color = 'red' if getattr(row, 'result') == 'failed' else 'green'

            if dur != 0:
                xranges.append((begin, dur))
                colors.append(color)
            else:
                plt.plot(begin, i + 0.25, marker='o', markerfacecolor=color, markeredgecolor=color, markersize=10)

        yticks.append(i + 0.25)
        yticklabels.append(
            f'{class_name}.{method_name}' if pd.isna(test_number) else f'{class_name}.{method_name}[{int(test_number)}]'
        )

        plt.broken_barh(xranges=xranges, yrange=(i, 0.5), facecolors=colors)
        i += 1

    ax.set_yticks(yticks)
    ax.set_yticklabels(yticklabels)
    ax.invert_yaxis()

    for value, begin, end in duplicate_attempts:
        if value and begin == end:
            ax.axvline(begin, color='black', lw=2, alpha=0.5)

        if value and begin != end:
            ax.axvspan(begin, end, alpha=0.5, color='black')

    # TODO
    ax.set_xticks(range(1, timeline['end'].max() + 1))

    st.pyplot(fig)


def main():
    submissions_path = st.text_input('Submissions path:')
    if not submissions_path:
        st.info('You should enter the submissions path.')
        st.stop()

    submissions = read_df(submissions_path)
    # TODO:
    submissions = submissions.dropna(subset=[EduColumnName.TESTS.value])

    group = st.number_input(
        'Group:',
        value=0,
        min_value=submissions[SubmissionColumns.GROUP.value].min(),
        max_value=submissions[SubmissionColumns.GROUP.value].max(),
    )

    group_submissions = submissions[submissions[SubmissionColumns.GROUP.value] == group]

    if len(group_submissions) == 0:
        st.error("It's a theory group.")
        st.stop()

    duplicate_indices = accumulate_results(group_submissions[EduColumnName.CODE_SNIPPETS.value].shift() == group_submissions[EduColumnName.CODE_SNIPPETS.value])

    tests_timeline = convert_parametrized_tests_to_timeline(group_submissions)

    plot_general(tests_timeline, duplicate_indices)

    parametrized_tests_timeline = tests_timeline[~pd.isna(tests_timeline[TestDataField.TEST_NUMBER.value])]
    if len(parametrized_tests_timeline) != 0:
        selected_name = st.selectbox(
            'Parametrized test name:',
            options=parametrized_tests_timeline[[TestDataField.CLASS_NAME.value, TestDataField.METHOD_NAME.value]]
            .drop_duplicates()
            .itertuples(index=False, name=None),
        )

        class_name, method_name = selected_name

        parametrized_test_timeline = parametrized_tests_timeline[
            (parametrized_tests_timeline[TestDataField.CLASS_NAME.value] == class_name)
            & (parametrized_tests_timeline[TestDataField.METHOD_NAME.value] == method_name)
        ]

        plot(parametrized_test_timeline, duplicate_indices)


if __name__ == '__main__':
    main()
