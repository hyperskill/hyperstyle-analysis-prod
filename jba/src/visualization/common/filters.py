from typing import Tuple

import pandas as pd
import streamlit as st
from core.src.model.column_name import SubmissionColumns
from jba.src.models.edu_columns import EduColumnName, EduTaskStatus
from jba.src.visualization.common.utils import get_edu_name_columns, ALL_CHOICE_OPTIONS


def _fix_submissions_after_filtering(submissions: pd.DataFrame) -> pd.DataFrame:
    fixed_submissions = submissions.reset_index(drop=True)
    fixed_submissions[SubmissionColumns.TOTAL_ATTEMPTS.value] = fixed_submissions[SubmissionColumns.GROUP.value].map(
        fixed_submissions.groupby(SubmissionColumns.GROUP.value).size()
    )
    return fixed_submissions


def filter_post_correct_submissions(submissions: pd.DataFrame) -> pd.DataFrame:
    exclude_post_correct_submissions_flag = st.checkbox(
        'Exclude post-correct submissions',
        value=False,
        help=(
            'If checked, then all submissions within one group '
            'that occur after the first correct submissions will be ignored.'
        ),
    )

    if not exclude_post_correct_submissions_flag:
        return submissions

    filtered_df = submissions.groupby(SubmissionColumns.GROUP.value).apply(
        lambda group: group[group.index <= group[EduColumnName.STATUS.value].eq(EduTaskStatus.CORRECT.value).idxmax()]
        if EduTaskStatus.CORRECT.value in group[EduColumnName.STATUS.value].unique()
        else group
    )

    return _fix_submissions_after_filtering(filtered_df)


def filter_duplicate_submissions(submissions: pd.DataFrame) -> pd.DataFrame:
    filter_duplicate_submissions_flag = st.checkbox('Exclude duplicate submissions', value=False)

    if not filter_duplicate_submissions_flag:
        return submissions

    filtered_df = submissions.groupby(SubmissionColumns.GROUP.value, as_index=False).apply(
        lambda group: group.loc[
            group[EduColumnName.CODE_SNIPPETS.value].shift() != group[EduColumnName.CODE_SNIPPETS.value]
        ]
    )

    return _fix_submissions_after_filtering(filtered_df)


def filter_invalid_submissions(submissions: pd.DataFrame) -> pd.DataFrame:
    filter_invalid_submissions_flag = st.checkbox(
        'Exclude invalid submissions',
        value=False,
        help='If checked, then all submissions within one group, that have compile exceptions will be ignored.',
    )

    if not filter_invalid_submissions_flag:
        return submissions

    filtered_df = submissions.groupby(SubmissionColumns.GROUP.value, as_index=False).apply(
        # Leave submission if it has no exceptions or a list of them is empty.
        lambda group: group[group[EduColumnName.EXCEPTIONS.value].eq('[]', fill_value='[]')]
    )

    return _fix_submissions_after_filtering(filtered_df)


def filter_by_edu_columns(course_structure, submissions) -> Tuple[str, Tuple[str], pd.DataFrame]:
    edu_name_columns = get_edu_name_columns(submissions)

    show_stats_for = st.radio('Show stats for: ', options=edu_name_columns, horizontal=True)
    edu_name_columns = edu_name_columns[: edu_name_columns.index(show_stats_for) + 1]

    # If the length of the edu_name_columns variable is larger than 1,
    # then groups will be tuples, else they will be strings ...
    grouped_submissions = submissions.groupby(edu_name_columns)

    options = filter(
        # ... and therefore we need to squeeze single element tuples.
        lambda name: name in grouped_submissions.groups if len(name) > 1 else name[0] in grouped_submissions.groups,
        course_structure[edu_name_columns].drop_duplicates().itertuples(index=False, name=None),
    )

    selection = st.selectbox(
        f'{show_stats_for}:',
        options=[ALL_CHOICE_OPTIONS, *options],
        format_func=lambda option: option if option == ALL_CHOICE_OPTIONS else '/'.join(option),
    )

    selection = selection if len(selection) > 1 or selection == ALL_CHOICE_OPTIONS else selection[0]
    submissions = submissions if selection == ALL_CHOICE_OPTIONS else grouped_submissions.get_group(selection)

    return show_stats_for, selection, submissions


def filter_by_task(
    submissions: pd.DataFrame,
    course_structure: pd.DataFrame,
    with_all_option: bool = False,
) -> Tuple[Tuple[str] | str, pd.DataFrame]:
    edu_name_columns = get_edu_name_columns(submissions)
    submissions_by_task = submissions.groupby(edu_name_columns)

    tasks = filter(
        lambda name: name in submissions_by_task.groups,
        course_structure[edu_name_columns].itertuples(index=False, name=None),
    )

    task = st.selectbox(
        'Task:',
        options=[ALL_CHOICE_OPTIONS, *tasks] if with_all_option else tasks,
        format_func=lambda option: option if option == ALL_CHOICE_OPTIONS else '/'.join(option),
    )

    return task, submissions if task == ALL_CHOICE_OPTIONS else submissions_by_task.get_group(task)


def filter_by_group(submissions: pd.DataFrame) -> Tuple[int, pd.DataFrame]:
    group = st.selectbox('Group:', options=submissions[SubmissionColumns.GROUP.value].unique())
    return group, submissions[submissions[SubmissionColumns.GROUP.value] == group].reset_index(drop=True)


def filter_by_user(submissions: pd.DataFrame):
    user_id = st.text_input('User ID:')
    if user_id == '':
        return submissions

    return submissions[submissions[SubmissionColumns.USER_ID.value] == user_id]


def filter_by_number_of_attempts(submissions: pd.DataFrame) -> Tuple[int, pd.DataFrame]:
    available_numbers_of_attempts = sorted(submissions.groupby(SubmissionColumns.GROUP.value).size().unique())
    number_of_attempts = st.selectbox('Number of attempts:', available_numbers_of_attempts)

    group_mask = submissions.groupby(SubmissionColumns.GROUP.value).size() == number_of_attempts

    return (
        number_of_attempts,
        submissions[submissions[SubmissionColumns.GROUP.value].isin(group_mask[group_mask].index)],
    )
