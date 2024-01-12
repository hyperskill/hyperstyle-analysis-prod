from typing import Callable

import pandas as pd
import streamlit as st

from jba.src.visualization.common.filters import filter_by_task, filter_by_group
from jba.src.visualization.common.utils import get_edu_name_columns
from jba.src.visualization.common.widgets import show_group_info, select_file, select_view_type, show_code_viewer


def filter_submissions_and_show_code_viewer(submissions: pd.DataFrame, course_structure: pd.DataFrame):
    columns = st.columns([2, 1, 2, 1])

    with columns[0]:
        _, submissions = filter_by_task(submissions, course_structure)
        group_info_placeholder = st.empty()

    with columns[1]:
        _, submissions = filter_by_group(submissions)
        with group_info_placeholder, st.expander('Group info'):
            show_group_info(submissions)

    with columns[2]:
        file = select_file(submissions)

    with columns[3]:
        view_type = select_view_type()

    show_code_viewer(submissions, view_type, file)


def convert_suspicious_tasks_to_markdown_list(
    tasks: pd.DataFrame,
    value_format_function: Callable[[pd.Series], str],
) -> str:
    edu_name_columns = get_edu_name_columns(tasks)
    return '\n'.join(
        tasks.apply(lambda row: f'* {"/".join(row[edu_name_columns])} – {value_format_function(row)}', axis=1)
    )
