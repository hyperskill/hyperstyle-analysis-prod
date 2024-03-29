from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st
from diff_viewer import diff_viewer

from core.src.model.column_name import SubmissionColumns
from core.src.utils.df_utils import read_df
from jba.src.inspections.analysis import (
    find_unique_inspections,
    get_inspections_stats,
    get_inspection_fixing_examples,
)
from jba.src.models.edu_columns import EduColumnName
from jba.src.visualization.common.filters import filter_by_task
from jba.src.visualization.common.utils import ALL_CHOICE_OPTIONS, read_submissions, fix_submissions_after_filtering
from jba.src.visualization.common.widgets import select_file, show_submission_postprocess_filters


def plot_inspections_stats(stats: pd.DataFrame, top: int, normalize: bool):
    title = 'Inspections frequency'

    if top != len(stats):
        title = f'{title} (top {top})'
        stats = stats.head(top)

    fig = px.bar(
        stats,
        y=['Fixed', 'Partially fixed', 'Not fixed'],
        color_discrete_map={'Fixed': 'green', 'Partially fixed': 'yellow', 'Not fixed': 'red'},
        title=title,
    )

    y_title = 'Groups'
    if normalize:
        y_title = f'{y_title} (%)'

    fig.update_yaxes(title=y_title)
    fig.update_legends(title='State')

    st.plotly_chart(fig, use_container_width=True)


@st.cache_data(show_spinner='Looking for examples... :eyes:')
def find_examples(submissions: pd.DataFrame, inspection: str, file: Optional[str]) -> pd.DataFrame:
    return (
        submissions.groupby(SubmissionColumns.GROUP.value)
        .apply(lambda group: get_inspection_fixing_examples(group, inspection, file))
        .explode()
        .dropna()
        .reset_index(drop=True)
    )


def main():
    st.set_page_config(page_title='Inspections stats', layout='wide')
    st.title('Inspections stats')

    filters = show_submission_postprocess_filters()
    submissions = read_submissions(st.session_state.submissions_path, filters)
    course_structure = read_df(st.session_state.course_structure_path)

    submissions = submissions.dropna(subset=[EduColumnName.INSPECTIONS.value])
    submissions = fix_submissions_after_filtering(submissions)

    left, right = st.columns([3, 1])

    with left:
        task, submissions = filter_by_task(submissions, course_structure, with_all_option=True)

    with right:
        file = select_file(submissions, disabled=task == ALL_CHOICE_OPTIONS, with_all_option=True)

    with st.expander('Config:'):
        left, right = st.columns([3, 1])

        with left:
            inspections_to_ignore = st.text_input(
                'Inspections to ignore:',
                help=(
                    'List of inspections to ignore. '
                    'Must be a string with the list of inspections seperated with comma.'
                ),
                value='KDocMissingDocumentation,UnusedSymbol',
            ).split(',')

        with right:
            number_of_inspections = len(find_unique_inspections(submissions, file) - set(inspections_to_ignore))

            top = st.number_input(
                'Top:',
                min_value=1,
                max_value=number_of_inspections,
                value=min(10, number_of_inspections),
            )

            normalize = st.checkbox('Normalize data', value=True)

    inspections_stats = get_inspections_stats(submissions, file, inspections_to_ignore, normalize)
    plot_inspections_stats(inspections_stats, top=top, normalize=normalize)

    inspections_to_choose = inspections_stats.head(top).index[
        inspections_stats.head(top)['Total'] != inspections_stats.head(top)['Not fixed']
    ]

    if inspections_to_choose.empty:
        st.stop()

    st.subheader('Inspections fixing', help='This section shows how students fix inspections')

    left, middle, right = st.columns([3, 1, 1])

    with left:
        inspection = st.selectbox('Inspection:', options=inspections_to_choose)
        examples = find_examples(submissions, inspection, file)

    with middle:
        example_number = st.number_input('Example:', min_value=0, max_value=len(examples) - 1)
        example = examples.iat[example_number]

    with right:
        st.metric(
            label='Number of inspections:',
            value=len(example.issues_after),
            delta=len(example.issues_after) - len(example.issues_before),
        )

    if task == ALL_CHOICE_OPTIONS:
        st.write(f'**Task**: {example.task_name}')

    if file is None:
        st.write(f'**File**: {example.file_path}')

    left, right = st.columns(2)

    with left:
        st.json([{'Line': issue.line_number, 'Description': issue.text} for issue in example.issues_before])

    with right:
        st.json([{'Line': issue.line_number, 'Description': issue.text} for issue in example.issues_after])

    diff_viewer(example.code_before, example.code_after, lang=None)


if __name__ == '__main__':
    main()
