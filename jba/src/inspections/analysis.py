from collections import Counter
from dataclasses import dataclass
from itertools import islice
from typing import Set, List, Optional, Dict

import pandas as pd

from core.src.model.column_name import SubmissionColumns
from core.src.model.quality.issue.hyperstyle_issue import HyperstyleIssue
from jba.src.models.edu_columns import EduColumnName
from jba.src.visualization.common import get_edu_name_columns


def find_unique_inspections(group: pd.DataFrame, file: Optional[str]) -> Set[str]:
    group_inspections = group[EduColumnName.INSPECTIONS.value].apply(
        lambda inspections: {
            inspection.code
            for file_path, file_inspections in inspections.items()
            for inspection in file_inspections
            if file is None or file_path == file
        }
    )

    return set(group_inspections.explode().unique())


def find_fixed_unique_inspections(group: pd.DataFrame, file: Optional[str]) -> Set[str]:
    unique_inspections = find_unique_inspections(group, file)

    last_attempt = group.loc[group[SubmissionColumns.ATTEMPT.value].idxmax()].squeeze()
    last_attempt_inspections = {
        inspection.code
        for file_path, file_inspections in last_attempt[EduColumnName.INSPECTIONS.value].items()
        for inspection in file_inspections
        if file is None or file_path == file
    }

    return unique_inspections - last_attempt_inspections


def find_not_fixed_unique_inspections(group: pd.DataFrame, file: Optional[str]) -> Set[str]:
    not_fixed_unique_inspections = find_unique_inspections(group, file)

    for previous_row, current_row in zip(group.itertuples(index=False), islice(group.itertuples(index=False), 1, None)):
        previous_number_of_inspections = Counter(
            inspection.code
            for file_path, file_inspections in getattr(previous_row, EduColumnName.INSPECTIONS.value).items()
            for inspection in file_inspections
            if file is None or file_path == file
        )

        current_number_of_inspections = Counter(
            inspection.code
            for file_path, file_inspections in getattr(current_row, EduColumnName.INSPECTIONS.value).items()
            for inspection in file_inspections
            if file is None or file_path == file
        )

        for inspection in previous_number_of_inspections.keys() | current_number_of_inspections.keys():
            if current_number_of_inspections.get(inspection, 0) < previous_number_of_inspections.get(inspection, 0):
                not_fixed_unique_inspections.discard(inspection)

    return not_fixed_unique_inspections


def get_unique_inspections_stats(
    df: pd.DataFrame,
    file: Optional[str],
    inspections_to_ignore: List[str],
    normalize: bool = True,
) -> pd.DataFrame:
    unique_inspections = (
        df.groupby(SubmissionColumns.GROUP.value)
        .apply(lambda group: find_unique_inspections(group, file))
        .explode()
        .value_counts()
    )

    unique_inspections.name = 'Total'

    fixed_unique_inspections = (
        df.groupby(SubmissionColumns.GROUP.value)
        .apply(lambda group: find_fixed_unique_inspections(group, file))
        .explode()
        .value_counts()
    )

    fixed_unique_inspections.name = 'Fixed'

    not_fixed_unique_inspections = (
        df.groupby(SubmissionColumns.GROUP.value)
        .apply(lambda group: find_not_fixed_unique_inspections(group, file))
        .explode()
        .value_counts()
    )

    not_fixed_unique_inspections.name = 'Not fixed'

    stats = (
        pd.concat(
            [unique_inspections, fixed_unique_inspections, not_fixed_unique_inspections],
            axis=1,
        )
        .fillna(0)
        .convert_dtypes()
    )

    stats['Partially fixed'] = stats['Total'] - stats['Fixed'] - stats['Not fixed']

    stats = stats[~stats.index.isin(inspections_to_ignore)]
    stats.index.name = 'Inspection'

    if normalize:
        stats = stats / df[SubmissionColumns.GROUP.value].nunique() * 100

    return stats


@dataclass
class FixingExample:
    task_name: str
    file_path: str
    before_issues: List[HyperstyleIssue]
    before_code: str
    after_issues: List[HyperstyleIssue]
    after_code: str


def _find_code_snippet(code_snippets: List[Dict[str, str]], file: str) -> str:
    return next(filter(lambda snippet: file == snippet['name'], code_snippets))['text']


def get_inspection_fixing_examples(
    group: pd.DataFrame,
    inspection_name: str,
    file: Optional[str],
) -> List[FixingExample]:
    edu_name_columns = get_edu_name_columns(group)
    task_name = "/".join(group[edu_name_columns].values[0])

    examples = []

    for previous_row, current_row in zip(group.itertuples(index=False), islice(group.itertuples(index=False), 1, None)):
        previous_issues_per_file = {
            file_path: [inspection for inspection in file_inspections if inspection.code == inspection_name]
            for file_path, file_inspections in getattr(previous_row, EduColumnName.INSPECTIONS.value).items()
            if file is None or file_path == file
        }

        current_issues_per_file = {
            file_path: [inspection for inspection in file_inspections if inspection.code == inspection_name]
            for file_path, file_inspections in getattr(current_row, EduColumnName.INSPECTIONS.value).items()
            if file is None or file_path == file
        }

        for file_path in previous_issues_per_file.keys():
            previous_issues = previous_issues_per_file[file_path]
            current_issues = current_issues_per_file[file_path]

            if len(current_issues) < len(previous_issues):
                previous_code = _find_code_snippet(getattr(previous_row, EduColumnName.CODE_SNIPPETS.value), file_path)
                current_code = _find_code_snippet(getattr(current_row, EduColumnName.CODE_SNIPPETS.value), file_path)
                examples.append(
                    FixingExample(task_name, file_path, previous_issues, previous_code, current_issues, current_code)
                )

    return examples
