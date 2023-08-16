from dataclasses import dataclass
from pathlib import Path
from typing import List, Callable

from dataclasses_json import dataclass_json

from core.src.model.quality.issue.hyperstyle_issue import HyperstyleIssue
from core.src.model.quality.issue.issue import BaseIssue
from core.src.model.quality.report import BaseReport
from core.src.model.report.quality_report import QualityReport
from core.src.utils.json_utils import parse_json


@dataclass_json
@dataclass(frozen=True, eq=True)
class HyperstyleReport(QualityReport, BaseReport):
    issues: List[HyperstyleIssue]

    def get_issues(self) -> List[HyperstyleIssue]:
        return self.issues

    def filter_issues(self, predicate: Callable[[BaseIssue], bool]) -> 'HyperstyleReport':
        # TODO: recalculate quality after filtering
        return HyperstyleReport(issues=[issue for issue in self.issues if predicate(issue)],
                                quality=self.quality)

    @staticmethod
    def from_file(json_path: Path) -> 'HyperstyleReport':
        return HyperstyleReport.from_dict(parse_json(json_path))


@dataclass_json
@dataclass(frozen=True, eq=True)
class HyperstyleFileReport(HyperstyleReport):
    file_name: str

    def to_hyperstyle_report(self) -> HyperstyleReport:
        return HyperstyleReport(self.quality, self.issues)


@dataclass_json
@dataclass(frozen=True, eq=True)
class HyperstyleNewFormatReport(QualityReport):
    file_review_results: List[HyperstyleFileReport]

    @staticmethod
    def from_file(json_path: Path) -> 'HyperstyleNewFormatReport':
        return HyperstyleNewFormatReport.from_dict(parse_json(json_path))
