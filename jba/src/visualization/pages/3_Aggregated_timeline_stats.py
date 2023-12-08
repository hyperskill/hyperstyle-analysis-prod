import numpy as np
import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt

from core.src.model.column_name import SubmissionColumns
from core.src.utils.df_utils import read_df
from jba.src.models.edu_columns import EduColumnName
from jba.src.models.edu_logs import TestDataField, TestResult
from jba.src.visualization.common import (
    convert_tests_to_timeline,
    aggregate_tests_timeline,
    START_COLUMN,
    FINISH_COLUMN,
    show_exclude_post_correct_submissions_flag,
    show_filter_by_task,
)


# https://matplotlib.org/stable/gallery/images_contours_and_fields/image_annotated_heatmap.html#using-the-helper-function-code-style
def heatmap(data, row_labels, col_labels, ax=None, cbar_kw=None, cbarlabel="", clim=(0, 1), **kwargs):
    if ax is None:
        ax = plt.gca()

    if cbar_kw is None:
        cbar_kw = {}

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)
    im.set_clim(*clim)  # TODO: ???

    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

    # Show all ticks and label them with the respective list entries.
    ax.set_xticks(np.arange(data.shape[1]), labels=col_labels)
    ax.set_yticks(np.arange(data.shape[0]), labels=row_labels)

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=-30, ha="right", rotation_mode="anchor")

    # Turn spines off and create white grid.
    ax.spines[:].set_visible(False)

    ax.set_xticks(np.arange(data.shape[1] + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0] + 1) - 0.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)

    return im, cbar


def pivot_tests(group: pd.DataFrame, number_of_submissions: int, aggregate: bool = True) -> pd.DataFrame:
    tests_timeline = convert_tests_to_timeline(group)
    if aggregate:
        tests_timeline = aggregate_tests_timeline(tests_timeline)

    exploded_tests_timeline = pd.DataFrame(
        [
            (
                getattr(row, TestDataField.CLASS_NAME.value),
                getattr(row, TestDataField.METHOD_NAME.value),
                getattr(row, TestDataField.TEST_NUMBER.value),
                getattr(row, TestDataField.RESULT.value),
                i,
            )
            for row in tests_timeline.itertuples()
            for i in range(getattr(row, START_COLUMN), getattr(row, FINISH_COLUMN) + 1)
        ],
        columns=[
            TestDataField.CLASS_NAME.value,
            TestDataField.METHOD_NAME.value,
            TestDataField.TEST_NUMBER.value,
            TestDataField.RESULT.value,
            'submission_number',
        ],
    )

    pivoted_tests = (
        exploded_tests_timeline.pivot(
            index=[TestDataField.CLASS_NAME.value, TestDataField.METHOD_NAME.value, TestDataField.TEST_NUMBER.value],
            columns='submission_number',
            values=TestDataField.RESULT.value,
        )
        .replace({TestResult.FAILED: 0, TestResult.PASSED: 1, None: 0})
        .convert_dtypes()
    )

    if pivoted_tests.columns.tolist() != list(range(1, number_of_submissions + 1)):
        columns_to_add = set(range(1, number_of_submissions + 1)) - set(pivoted_tests.columns.tolist())
        for column in columns_to_add:
            pivoted_tests[column] = None

        pivoted_tests = pivoted_tests.reindex(range(1, number_of_submissions + 1), axis=1)

    return pivoted_tests


def convert_tests_to_chain(group: pd.DataFrame, aggregate: bool = True) -> pd.DataFrame:
    pivoted_tests = pivot_tests(group, aggregate)
    return pivoted_tests.diff(axis=1).fillna(pivoted_tests)


def main():
    st.title('Aggregated timeline stats')

    submissions = read_df(st.session_state.submissions_path)
    course_structure = read_df(st.session_state.course_structure_path)

    submissions = submissions[submissions.task_type != 'theory']

    submissions = (
        submissions.groupby(SubmissionColumns.GROUP.value, as_index=False)
        .apply(
            lambda group: group.loc[
                group[EduColumnName.CODE_SNIPPETS.value].shift() != group[EduColumnName.CODE_SNIPPETS.value]
            ]
        )
        .droplevel(0)
    )

    submissions = (
        submissions.groupby(SubmissionColumns.GROUP.value, as_index=False)
        .apply(lambda group: group.loc[~pd.isna(group[EduColumnName.TESTS.value])])
        .droplevel(0)
    )

    submissions = show_exclude_post_correct_submissions_flag(submissions)

    left, right = st.columns([3, 1])

    with left:
        task, task_submissions = show_filter_by_task(submissions, course_structure)
        number_of_groups_in_task = len(task_submissions[SubmissionColumns.GROUP.value].unique())

    with right:
        available_numbers_of_attempts = sorted(task_submissions.groupby(SubmissionColumns.GROUP.value).size().unique())
        number_of_attempts = st.selectbox('Number of attempts:', available_numbers_of_attempts)

    group_mask = task_submissions.groupby(SubmissionColumns.GROUP.value).size() == number_of_attempts
    task_submissions_with_attempt = task_submissions[
        task_submissions[SubmissionColumns.GROUP.value].isin(group_mask[group_mask].index)
    ]
    number_of_groups_in_task_attempt = len(task_submissions_with_attempt[SubmissionColumns.GROUP.value].unique())

    with st.expander('Description:'):
        st.write(f'Stats for {number_of_groups_in_task_attempt} groups out of {number_of_groups_in_task}')
        st.write(f'Groups: {group_mask[group_mask].index.tolist()}')

    # TODO: gray out tests from previous tasks
    # TODO: show chart for parametrized tests

    st.subheader(
        'Average tests timeline',
        help=(
            f'This graph shows the average test timeline for all {"/".join(task)} timelines '
            f'with number of attempts equal to {number_of_attempts}.'
        ),
    )

    pivoted_res = None
    for name, group in task_submissions_with_attempt.groupby([SubmissionColumns.GROUP.value]):
        pivoted_tests = pivot_tests(group, number_of_attempts)
        if pivoted_res is None:
            pivoted_res = pivoted_tests.fillna(0)
            continue

        pivoted_res += pivoted_tests.fillna(0)

    fig, ax = plt.subplots()
    data = (pivoted_res / pivoted_res.max(None)).to_numpy(dtype=float)
    im, cbar = heatmap(
        data,
        pivoted_res.index.map(lambda x: '.'.join(y for y in x if not pd.isna(y))),
        range(1, number_of_attempts + 1),
        ax=ax,
        cmap="RdYlGn",
        cbarlabel="Passed (%)",
    )
    ax.set_xlabel('Attempt')
    fig.tight_layout()
    st.pyplot(fig)

    st.subheader(
        'Chain',
        help=(
            'This graph shows in what order the tests were fixed (or broken) '
            f'in all {"/".join(task)} groups with the number of attempts equal to {number_of_attempts}.'
        ),
    )

    with st.expander('Legend'):
        st.markdown(
            """
            * :green[1] means that all groups on the current attempt have fixed a particular test
            * 0 means that
                - either the status of the test has not changed
                - or the number of groups in which the test was fixed and broken are the same
            * :red[-1] means that all groups on the current attempt have broken a particular test
            """
        )  # noqa: WPS355

    chained_res = None
    for name, group in task_submissions_with_attempt.groupby([SubmissionColumns.GROUP.value]):
        chained_tests = convert_tests_to_chain(group, number_of_attempts)
        if chained_res is None:
            chained_res = chained_tests
            continue

        chained_res += chained_tests

    fig, ax = plt.subplots()
    data = (chained_res / chained_res.abs().max(None)).to_numpy(dtype=float)
    im, cbar = heatmap(
        data,
        chained_res.index.map(lambda x: '.'.join(y for y in x if not pd.isna(y))),
        range(1, number_of_attempts + 1),
        ax=ax,
        cmap="RdYlGn",
        clim=(-1, 1),
    )
    ax.set_xlabel('Attempt')
    fig.tight_layout()
    st.pyplot(fig)


if __name__ == '__main__':
    main()
