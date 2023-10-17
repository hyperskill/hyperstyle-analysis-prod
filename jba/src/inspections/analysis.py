from collections import Counter
from itertools import islice
from typing import Set, List, Tuple

import pandas as pd

from core.src.model.column_name import SubmissionColumns
from core.src.model.quality.issue.hyperstyle_issue import HyperstyleIssue
from jba.src.models.edu_columns import EduColumnName


def find_unique_inspections(group: pd.DataFrame) -> Set[str]:
    return set(
        group[EduColumnName.INSPECTIONS.value]
        .apply(lambda inspections: {inspection.code for inspection in inspections})
        .explode()
        .unique()
    )


def find_fixed_unique_inspections(group: pd.DataFrame) -> Set[str]:
    unique_inspections = find_unique_inspections(group)

    last_attempt = group.loc[group[SubmissionColumns.ATTEMPT.value].idxmax()].squeeze()
    last_attempt_inspections = {inspection.code for inspection in last_attempt[EduColumnName.INSPECTIONS.value]}

    return unique_inspections - last_attempt_inspections


def find_not_fixed_unique_inspections(group: pd.DataFrame) -> Set[str]:
    not_fixed_unique_inspections = find_unique_inspections(group)

    for previous_row, current_row in zip(group.itertuples(index=False), islice(group.itertuples(index=False), 1, None)):
        previous_number_of_inspections = Counter(
            inspection.code for inspection in getattr(previous_row, EduColumnName.INSPECTIONS.value)
        )

        current_number_of_inspections = Counter(
            inspection.code for inspection in getattr(current_row, EduColumnName.INSPECTIONS.value)
        )

        for inspection in previous_number_of_inspections.keys() | current_number_of_inspections.keys():
            if current_number_of_inspections.get(inspection, 0) < previous_number_of_inspections.get(inspection, 0):
                not_fixed_unique_inspections.discard(inspection)

    return not_fixed_unique_inspections


def get_unique_inspections_stats(
    df: pd.DataFrame,
    inspections_to_ignore: List[str],
    normalize: bool = True,
) -> pd.DataFrame:
    unique_inspections = (
        df.groupby(SubmissionColumns.GROUP.value).apply(find_unique_inspections).explode().value_counts()
    )

    unique_inspections.name = 'Total'

    fixed_unique_inspections = (
        df.groupby(SubmissionColumns.GROUP.value).apply(find_fixed_unique_inspections).explode().value_counts()
    )

    fixed_unique_inspections.name = 'Fixed'

    not_fixed_unique_inspections = (
        df.groupby(SubmissionColumns.GROUP.value).apply(find_not_fixed_unique_inspections).explode().value_counts()
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


def get_inspection_fixing_examples(  # noqa: WPS234
    group: pd.DataFrame,
    inspection_name: str,
) -> List[Tuple[List[HyperstyleIssue], str, List[HyperstyleIssue], str]]:
    examples = []

    for previous_row, current_row in zip(group.itertuples(index=False), islice(group.itertuples(index=False), 1, None)):
        previous_issues = [
            inspection
            for inspection in getattr(previous_row, EduColumnName.INSPECTIONS.value)
            if inspection.code == inspection_name
        ]

        current_issues = [
            inspection
            for inspection in getattr(current_row, EduColumnName.INSPECTIONS.value)
            if inspection.code == inspection_name
        ]

        if len(previous_issues) - len(current_issues) > 0:
            previous_code = getattr(previous_row, EduColumnName.CODE_SNIPPETS.value)
            current_code = getattr(current_row, EduColumnName.CODE_SNIPPETS.value)
            examples.append((previous_issues, previous_code, current_issues, current_code))

    return examples
