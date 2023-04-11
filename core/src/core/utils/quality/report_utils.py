import logging

import pandas as pd
from hyperstyle.src.python.review.application_config import LanguageVersion

from core.model.column_name import SubmissionColumns
from core.model.quality.report import BaseReport
from core.model.report.hyperstyle_report import HyperstyleReport
from core.model.report.qodana_report import QodanaReport

logger = logging.getLogger(__name__)


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


def get_language_version(lang_key: str) -> LanguageVersion:
    try:
        return LanguageVersion(lang_key)
    except ValueError as e:
        # We should raise KeyError since it is incorrect value for key in a column
        raise KeyError(e)
