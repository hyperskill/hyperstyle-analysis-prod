import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

import pandas as pd
import streamlit as st

from core.src.model.column_name import SubmissionColumns
from core.src.model.report.hyperstyle_report import HyperstyleReport
from jba.src.models.edu_columns import EduColumnName, EduTaskStatus
from jba.src.models.edu_logs import TestData, ExceptionData

ALL_CHOICE_OPTIONS = 'All'


def fix_submissions_after_filtering(submissions: pd.DataFrame) -> pd.DataFrame:
    fixed_submissions = submissions.reset_index(drop=True)
    fixed_submissions[SubmissionColumns.TOTAL_ATTEMPTS.value] = fixed_submissions[SubmissionColumns.GROUP.value].map(
        fixed_submissions.groupby(SubmissionColumns.GROUP.value).size()
    )
    return fixed_submissions


@st.cache_data(show_spinner=False)
def _read_submissions(path: Path) -> pd.DataFrame:
    submissions = pd.read_csv(path)

    submissions[EduColumnName.CODE_SNIPPETS.value] = submissions[EduColumnName.CODE_SNIPPETS.value].apply(
        lambda code_snippets_dump: None if pd.isna(code_snippets_dump) else json.loads(code_snippets_dump)
    )

    submissions[EduColumnName.TESTS.value] = submissions[EduColumnName.TESTS.value].apply(
        lambda tests_dump: None if pd.isna(tests_dump) else TestData.schema().loads(tests_dump, many=True)
    )

    submissions[EduColumnName.EXCEPTIONS.value] = submissions[EduColumnName.EXCEPTIONS.value].apply(
        lambda exceptions_dump: None
        if pd.isna(exceptions_dump)
        else ExceptionData.schema().loads(exceptions_dump, many=True)
    )

    submissions[EduColumnName.INSPECTIONS.value] = submissions[EduColumnName.INSPECTIONS.value].apply(
        lambda inspections_dump: None
        if pd.isna(inspections_dump)
        else {
            file_path: HyperstyleReport.from_json(file_inspections).get_issues()
            for file_path, file_inspections in json.loads(inspections_dump).items()
        }
    )

    return submissions


@dataclass
class PostprocessFilters:
    exclude_post_correct_submissions: bool
    exclude_duplicate_submissions: bool
    exclude_invalid_submissions: bool


@st.cache_data(show_spinner='Reading submissions...')
def read_submissions(path: Path, filters: PostprocessFilters) -> pd.DataFrame:
    submissions = _read_submissions(path)

    if filters.exclude_post_correct_submissions:
        submissions = submissions.groupby(SubmissionColumns.GROUP.value, as_index=False).apply(
            lambda group: group[
                group.index <= group[EduColumnName.STATUS.value].eq(EduTaskStatus.CORRECT.value).idxmax()
            ]
            if EduTaskStatus.CORRECT.value in group[EduColumnName.STATUS.value].unique()
            else group
        )

        submissions = fix_submissions_after_filtering(submissions)

    if filters.exclude_invalid_submissions:
        submissions = submissions.groupby(SubmissionColumns.GROUP.value, as_index=False).apply(
            lambda group: group[
                ~group[EduColumnName.EXCEPTIONS.value].apply(
                    lambda exceptions: isinstance(exceptions, list) and exceptions
                )
            ]
        )

        submissions = fix_submissions_after_filtering(submissions)

    if filters.exclude_duplicate_submissions:
        submissions = submissions.groupby(SubmissionColumns.GROUP.value, as_index=False).apply(
            lambda group: group.loc[
                group[EduColumnName.CODE_SNIPPETS.value].shift() != group[EduColumnName.CODE_SNIPPETS.value]
            ]
        )

        submissions = fix_submissions_after_filtering(submissions)

    return submissions


def get_edu_name_columns(df: pd.DataFrame) -> List[str]:
    df_columns = df.columns.tolist()

    edu_name_columns = [
        EduColumnName.SECTION_NAME.value,
        EduColumnName.LESSON_NAME.value,
        EduColumnName.TASK_NAME.value,
    ]

    return [element for element in edu_name_columns if element in df_columns]


def find_duplicate_attempts(group: pd.DataFrame) -> List[int]:
    duplicate_mask = group[EduColumnName.CODE_SNIPPETS.value].shift() == group[EduColumnName.CODE_SNIPPETS.value]
    return (duplicate_mask[duplicate_mask].index.values + 1).tolist()


def find_invalid_attempts(group: pd.DataFrame) -> List[int]:
    invalid_mask = pd.isna(group[EduColumnName.TESTS.value])
    return (invalid_mask[invalid_mask].index.values + 1).tolist()
