from collections import Counter
from dataclasses import dataclass
from itertools import islice
from typing import Set, List, Optional, Dict, Callable

import pandas as pd

from core.src.model.column_name import SubmissionColumns
from core.src.model.quality.issue.hyperstyle_issue import HyperstyleIssue
from jba.src.models.edu_columns import EduColumnName
from jba.src.visualization.common.utils import get_edu_name_columns


def _filter_inspections(
    inspections_by_file: Dict[str, List[HyperstyleIssue]],
    inspection_name: Optional[str],
    file: Optional[str],
) -> Dict[str, List[HyperstyleIssue]]:
    return {
        file_path: [
            inspection
            for inspection in file_inspections
            if inspection_name is None or inspection.code == inspection_name
        ]
        for file_path, file_inspections in inspections_by_file.items()
        if file is None or file_path == file
    }


def _get_inspection_codes_by_file(
    inspections_by_file: Dict[str, List[HyperstyleIssue]],
    file: Optional[str],
) -> Set[str]:
    filtered_inspections = _filter_inspections(inspections_by_file, inspection_name=None, file=file)
    return {
        inspection.code
        for file_path, file_inspections in filtered_inspections.items()
        for inspection in file_inspections
    }


def find_unique_inspections(group: pd.DataFrame, file: Optional[str]) -> Set[str]:
    return set(
        group[EduColumnName.INSPECTIONS.value]
        .apply(lambda inspections: _get_inspection_codes_by_file(inspections, file))
        .explode()
        .unique()
    )


def find_fixed_unique_inspections(group: pd.DataFrame, file: Optional[str]) -> Set[str]:
    unique_inspections = find_unique_inspections(group, file)

    last_attempt = group.loc[group[SubmissionColumns.ATTEMPT.value].idxmax()].squeeze()
    last_attempt_inspections = _get_inspection_codes_by_file(last_attempt[EduColumnName.INSPECTIONS.value], file)

    return unique_inspections - last_attempt_inspections


def find_not_fixed_unique_inspections(group: pd.DataFrame, file: Optional[str]) -> Set[str]:
    not_fixed_unique_inspections = find_unique_inspections(group, file)

    for previous_row, current_row in zip(group.itertuples(index=False), islice(group.itertuples(index=False), 1, None)):
        previous_number_of_inspections = Counter(
            _get_inspection_codes_by_file(getattr(previous_row, EduColumnName.INSPECTIONS.value), file)
        )

        current_number_of_inspections = Counter(
            _get_inspection_codes_by_file(getattr(current_row, EduColumnName.INSPECTIONS.value), file)
        )

        for inspection in previous_number_of_inspections.keys() | current_number_of_inspections.keys():
            if current_number_of_inspections.get(inspection, 0) < previous_number_of_inspections.get(inspection, 0):
                not_fixed_unique_inspections.discard(inspection)

    return not_fixed_unique_inspections


def _gather_inspection_stats(
    df: pd.DataFrame,
    file: Optional[str],
    inspections_gatherer: Callable[[pd.DataFrame, Optional[str]], Set[str]],
) -> pd.Series:
    return (
        df.groupby(SubmissionColumns.GROUP.value)
        .apply(lambda group: inspections_gatherer(group, file))
        .explode()
        .value_counts()
    )


def get_inspections_stats(
    df: pd.DataFrame,
    file: Optional[str],
    inspections_to_ignore: List[str],
    normalize: bool = True,
) -> pd.DataFrame:
    unique_inspections = _gather_inspection_stats(df, file, find_unique_inspections)
    unique_inspections.name = 'Total'

    fixed_unique_inspections = _gather_inspection_stats(df, file, find_fixed_unique_inspections)
    fixed_unique_inspections.name = 'Fixed'

    not_fixed_unique_inspections = _gather_inspection_stats(df, file, find_not_fixed_unique_inspections)
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
class InspectionFixExample:
    task_name: str
    file_path: str
    issues_before: List[HyperstyleIssue]
    code_before: str
    issues_after: List[HyperstyleIssue]
    code_after: str


def find_code_snippet(code_snippets: List[Dict[str, str]], file: str) -> str:
    return next(filter(lambda snippet: file == snippet['name'], code_snippets))['text']


def get_inspection_fixing_examples(
    group: pd.DataFrame,
    inspection_name: str,
    file: Optional[str],
) -> List[InspectionFixExample]:
    edu_name_columns = get_edu_name_columns(group)
    task_name = "/".join(group[edu_name_columns].values[0])

    examples = []

    for previous_row, current_row in zip(group.itertuples(index=False), islice(group.itertuples(index=False), 1, None)):
        previous_issues_per_file = _filter_inspections(
            getattr(previous_row, EduColumnName.INSPECTIONS.value),
            inspection_name,
            file,
        )

        current_issues_per_file = _filter_inspections(
            getattr(current_row, EduColumnName.INSPECTIONS.value),
            inspection_name,
            file,
        )

        # We use an intersection here because it is possible that two neighboring submissions
        # may have different files (for example, in case when the course structure has been changed)
        for file_path in previous_issues_per_file.keys() & current_issues_per_file.keys():
            previous_issues = previous_issues_per_file[file_path]
            current_issues = current_issues_per_file[file_path]

            if len(current_issues) < len(previous_issues):
                previous_code = find_code_snippet(getattr(previous_row, EduColumnName.CODE_SNIPPETS.value), file_path)
                current_code = find_code_snippet(getattr(current_row, EduColumnName.CODE_SNIPPETS.value), file_path)
                examples.append(
                    InspectionFixExample(
                        task_name, file_path, previous_issues, previous_code, current_issues, current_code
                    )
                )

    return examples
