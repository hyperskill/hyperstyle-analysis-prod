import operator
from enum import Enum
from typing import Optional

import pandas as pd
import streamlit as st
from jba.src.models.edu_columns import EduColumnName
from jba.src.visualization.common.utils import ALL_CHOICE_OPTIONS


class ViewType(Enum):
    PER_SUBMISSION = 'Per submission'
    DIFFERENCE = 'Difference'


def select_view_type(disabled: bool = False) -> ViewType:
    return st.selectbox(
        'View type:',
        options=ViewType,
        format_func=lambda view_type: view_type.value,
        disabled=disabled,
    )


def select_file(submissions: pd.DataFrame, disabled: bool = False, with_all_option: bool = False) -> Optional[str]:
    options = map(
        operator.itemgetter('name'),
        submissions[EduColumnName.CODE_SNIPPETS.value].values[0],
    )

    file = st.selectbox(
        'File:',
        options=[ALL_CHOICE_OPTIONS, *options] if with_all_option else options,
        disabled=disabled,
    )

    if file == ALL_CHOICE_OPTIONS:
        return None

    return file
