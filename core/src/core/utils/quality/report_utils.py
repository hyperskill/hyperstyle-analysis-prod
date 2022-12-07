import pandas as pd

from core.model.column_name import SubmissionColumns
from core.model.quality.report import BaseReport
from core.model.report.hyperstyle_report import HyperstyleReport
from core.model.report.qodana_report import QodanaReport


def parse_str_report(str_report: str, column: str) -> BaseReport:
    """ Parse code quality report from json string `str_report` according to `column`. """

    if column == SubmissionColumns.HYPERSTYLE_ISSUES.value:
        return HyperstyleReport.from_json(str_report)
    if column == SubmissionColumns.QODANA_ISSUES.value:
        return QodanaReport.from_json(str_report)

    raise NotImplementedError(f'Implement parser for issue stored in column: {column}')


def parse_report(row: pd.Series, column: str) -> BaseReport:
    """ Parse code quality report from `row` stored in `column` as a json string. """

    return parse_str_report(row[column], column)

