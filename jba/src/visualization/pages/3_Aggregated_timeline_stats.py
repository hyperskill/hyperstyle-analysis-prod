import numpy as np
import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt

from core.src.model.column_name import SubmissionColumns
from core.src.utils.df_utils import read_df
from jba.src.models.edu_columns import EduColumnName, EduTaskType
from jba.src.test_logs.analysis import pivot_tests, convert_tests_to_chain, convert_test_results_to_numeral
from jba.src.visualization.common.filters import filter_by_task, filter_by_number_of_attempts
from jba.src.visualization.common.utils import read_submissions, fix_submissions_after_filtering
from jba.src.visualization.common.widgets import show_submission_postprocess_filters


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


def main():
    st.title('Aggregated timeline stats')

    filters = show_submission_postprocess_filters()
    submissions = read_submissions(st.session_state.submissions_path, filters)
    course_structure = read_df(st.session_state.course_structure_path)

    submissions = submissions[submissions[EduColumnName.TASK_TYPE.value] != EduTaskType.THEORY.value]

    submissions = submissions.groupby(SubmissionColumns.GROUP.value, as_index=False).apply(
        lambda group: group.loc[~pd.isna(group[EduColumnName.TESTS.value])]
    )

    submissions = fix_submissions_after_filtering(submissions)

    left, right = st.columns([3, 1])

    with left:
        task, submissions = filter_by_task(submissions, course_structure)
        number_of_groups_in_task = len(submissions[SubmissionColumns.GROUP.value].unique())

    with right:
        number_of_attempts, submissions = filter_by_number_of_attempts(submissions)
        attempt_groups = submissions[SubmissionColumns.GROUP.value].unique().tolist()

    with st.expander('Description:'):
        st.write(f'Stats for {len(attempt_groups)} groups out of {number_of_groups_in_task}')
        st.write(f'Groups: {attempt_groups}')

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
    for name, group in submissions.groupby(SubmissionColumns.GROUP.value):
        pivoted_tests = convert_test_results_to_numeral(pivot_tests(group, aggregate=True))
        if pivoted_res is None:
            pivoted_res = pivoted_tests.fillna(0)
            continue

        pivoted_res += pivoted_tests.fillna(0)

    fig, ax = plt.subplots()
    data = (pivoted_res / pivoted_res.max(None)).to_numpy(dtype=float)
    heatmap(
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
    for name, group in submissions.groupby(SubmissionColumns.GROUP.value):
        chained_tests = convert_tests_to_chain(group, number_of_attempts)
        if chained_res is None:
            chained_res = chained_tests
            continue

        chained_res += chained_tests

    fig, ax = plt.subplots()
    data = (chained_res / chained_res.abs().max(None)).to_numpy(dtype=float)
    heatmap(
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
