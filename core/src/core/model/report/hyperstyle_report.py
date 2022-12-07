from dataclasses import dataclass
from pathlib import Path
from typing import List, Callable

from dataclasses_json import dataclass_json

from core.model.quality.issue.hyperstyle_issue import HyperstyleIssue
from core.model.quality.issue.issue import BaseIssue
from core.model.quality.report import BaseReport
from core.model.report.quality_report import QualityReport
from core.utils.json_utils import parse_json


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
