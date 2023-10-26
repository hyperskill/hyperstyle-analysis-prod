import json
import operator
from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st
from diff_viewer import diff_viewer

from core.src.model.column_name import SubmissionColumns
from core.src.model.report.hyperstyle_report import HyperstyleReport
from core.src.utils.df_utils import read_df
from jba.src.inspections.analysis import (
    find_unique_inspections,
    get_unique_inspections_stats,
    get_inspection_fixing_examples,
)
from jba.src.models.edu_columns import EduColumnName
from jba.src.visualization.common import get_edu_name_columns

ALL_CHOICE_OPTIONS = 'All'


def plot_unique_inspections_stats(stats: pd.DataFrame, top: int, normalize: bool):
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


@st.cache_data
def read_submissions(path: Path) -> pd.DataFrame:
    submissions = read_df(path)
    submissions = submissions.dropna(subset=[EduColumnName.INSPECTIONS.value])

    submissions[EduColumnName.CODE_SNIPPETS.value] = submissions[EduColumnName.CODE_SNIPPETS.value].apply(json.loads)
    submissions[EduColumnName.INSPECTIONS.value] = submissions[EduColumnName.INSPECTIONS.value].apply(
        lambda inspections: {
            file_path: HyperstyleReport.from_json(file_inspections).get_issues()
            for file_path, file_inspections in json.loads(inspections).items()
        }
    )

    return submissions


@st.cache_data
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

    submissions = read_submissions(st.session_state.submissions_path)

    course_structure = read_df(st.session_state.course_structure_path)
    edu_name_columns = get_edu_name_columns(submissions)

    left, right = st.columns([3, 1])

    with left:
        submissions_by_task = submissions.groupby(edu_name_columns)

        tasks = filter(
            lambda name: name in submissions_by_task.groups,
            course_structure[edu_name_columns].itertuples(index=False, name=None),
        )

        task = st.selectbox(
            'Task:',
            options=[ALL_CHOICE_OPTIONS, *tasks],
            format_func=lambda option: option if option == ALL_CHOICE_OPTIONS else '/'.join(option),
        )

        task_submissions = submissions if task == ALL_CHOICE_OPTIONS else submissions_by_task.get_group(task)

    with right:
        file = st.selectbox(
            'File:',
            options=[
                ALL_CHOICE_OPTIONS,
                *map(
                    operator.itemgetter('name'),
                    task_submissions[EduColumnName.CODE_SNIPPETS.value].values[0],
                ),
            ],
            disabled=(task == ALL_CHOICE_OPTIONS),
        )

        if file == ALL_CHOICE_OPTIONS:
            file = None

    with st.expander('Config:'):
        left, right = st.columns(2)

        with left:
            top = st.number_input(
                'Top:',
                min_value=1,
                max_value=len(find_unique_inspections(task_submissions, file)),
                value=min(10, len(find_unique_inspections(task_submissions, file))),
            )

        with right:
            inspections_to_ignore = st.text_input(
                'Inspections to ignore:',
                help=(
                    'List of inspections to ignore. '
                    'Must be a string with the list of inspections seperated with comma.'
                ),
                value='KDocMissingDocumentation,UnusedSymbol',
            ).split(',')

    with st.sidebar:
        normalize = st.checkbox('Normalize data', value=True)

    unique_inspections_stats = get_unique_inspections_stats(task_submissions, file, inspections_to_ignore, normalize)
    plot_unique_inspections_stats(unique_inspections_stats, top=top, normalize=normalize)

    inspections_to_choose = unique_inspections_stats.head(top).index[
        unique_inspections_stats.head(top)['Total'] != unique_inspections_stats.head(top)['Not fixed']
    ]

    if inspections_to_choose.empty:
        st.stop()

    st.subheader('Inspections fixing', help='This section shows how students fix inspections')

    left, middle, right = st.columns([3, 1, 1])

    with left:
        inspection = st.selectbox('Inspection:', options=inspections_to_choose)
        examples = find_examples(task_submissions, inspection, file)

    with middle:
        example_number = st.number_input('Example:', min_value=0, max_value=len(examples) - 1)
        example = examples.iat[example_number]

    with right:
        st.metric(
            label='Number of inspections:',
            value=len(example.after_issues),
            delta=len(example.after_issues) - len(example.before_issues),
        )

    if task == ALL_CHOICE_OPTIONS:
        st.write(f'**Task**: {example.task_name}')

    if file is None:
        st.write(f'**File**: {example.file_path}')

    left, right = st.columns(2)

    with left:
        st.json([{'Line': issue.line_number, 'Description': issue.text} for issue in example.before_issues])

    with right:
        st.json([{'Line': issue.line_number, 'Description': issue.text} for issue in example.after_issues])

    diff_viewer(example.before_code, example.after_code, lang=None)


if __name__ == '__main__':
    main()
