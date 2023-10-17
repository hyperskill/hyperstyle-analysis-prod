import json
from pathlib import Path
from typing import List, Dict, Tuple

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

INSPECTIONS_TO_IGNORE = ['KDocMissingDocumentation', 'UnusedSymbol']


def plot_unique_inspections_stats(stats: pd.DataFrame, top: int):
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

    fig.update_yaxes(title='Groups')
    fig.update_legends(title='State')

    st.plotly_chart(fig, use_container_width=True)


# TODO: add support for multi file projects
def _find_kotlin_main_file(code_snippets: List[Dict[str, str]]) -> Tuple[str, str]:
    main_file = next(filter(lambda snippet: 'Main.kt' in snippet['name'], code_snippets))
    return main_file['name'], main_file['text']


def _prepare_submission(row: pd.Series) -> pd.Series:
    code_snippets = json.loads(row[EduColumnName.CODE_SNIPPETS.value])
    main_file_path, main_file_content = _find_kotlin_main_file(code_snippets)

    return pd.Series(
        [
            main_file_content,
            HyperstyleReport.from_json(json.loads(row[EduColumnName.INSPECTIONS.value])[main_file_path]).get_issues(),
        ],
        index=[EduColumnName.CODE_SNIPPETS.value, EduColumnName.INSPECTIONS.value],
    )


@st.cache_data
def read_submissions(path: Path):
    submissions = read_df(path)
    submissions = submissions.dropna(subset=[EduColumnName.INSPECTIONS.value])

    submissions[[EduColumnName.CODE_SNIPPETS.value, EduColumnName.INSPECTIONS.value]] = submissions.apply(
        _prepare_submission,
        axis=1,
    )

    return submissions


def main():
    st.set_page_config(page_title='Inspections stats', layout='wide')
    st.title('Inspections stats')

    submissions = read_submissions(st.session_state.submissions_path)

    left, right = st.columns([3, 1])

    with left:
        # TODO: handle absence of sections
        submissions_by_task = submissions.groupby(
            [EduColumnName.SECTION_NAME.value, EduColumnName.LESSON_NAME.value, EduColumnName.TASK_NAME.value]
        )

        task = st.selectbox(
            'Task:',
            options=['All', *submissions_by_task.groups],
            format_func=lambda option: '/'.join(option) if option in submissions_by_task.groups else option,
        )

        task_submissions = submissions_by_task.get_group(task) if task in submissions_by_task.groups else submissions

    with right:
        top = st.number_input(
            'Top:',
            min_value=1,
            max_value=len(find_unique_inspections(task_submissions)),
            value=min(10, len(find_unique_inspections(task_submissions))),
        )

    with st.sidebar:
        normalize = st.checkbox('Normalize data', value=True)

    unique_inspections_stats = get_unique_inspections_stats(task_submissions, INSPECTIONS_TO_IGNORE, normalize)
    plot_unique_inspections_stats(unique_inspections_stats, top=top)

    inspections_to_choose = unique_inspections_stats.head(top).index[
        unique_inspections_stats.head(top)['Total'] != unique_inspections_stats.head(top)['Not fixed']
    ]

    if not inspections_to_choose:
        st.stop()

    st.subheader('Inspections fixing', help='This section shows how students fix inspections')

    left, middle, right = st.columns([3, 1, 1])

    with left:
        inspection = st.selectbox('Inspection:', options=inspections_to_choose)

        examples = (
            task_submissions.groupby(SubmissionColumns.GROUP.value)
            .apply(lambda group: get_inspection_fixing_examples(group, inspection))
            .explode()
            .dropna()
            .reset_index(drop=True)
        )

    with middle:
        example_number = st.number_input('Example:', min_value=0, max_value=len(examples) - 1)
        previous_issues, previous_code, current_issues, current_code = examples.iat[example_number]

    with right:
        st.metric(
            label='Number of inspections:', value=len(current_issues), delta=len(current_issues) - len(previous_issues)
        )

    left, right = st.columns(2)

    with left:
        st.json([{'Line': issue.line_number, 'Description': issue.text} for issue in previous_issues])

    with right:
        st.json([{'Line': issue.line_number, 'Description': issue.text} for issue in current_issues])

    diff_viewer(previous_code, current_code, lang=None)


if __name__ == '__main__':
    main()
