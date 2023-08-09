from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Union

from dataclasses_json import dataclass_json, LetterCase

from core.src.model.quality.issue.issue import BaseIssue
from core.src.model.quality.issue.problem import Problem
from core.src.model.quality.report import BaseReport
from core.src.utils.json_utils import parse_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True, eq=True)
class QodanaReport(BaseReport):
    version: str
    list_problem: List[Problem]

    @staticmethod
    def get_default() -> 'QodanaReport':
        return QodanaReport("", [])

    def get_issues(self) -> List[Problem]:
        return self.list_problem

    def filter_issues(self, predicate: Callable[[BaseIssue], bool]) -> 'QodanaReport':
        return QodanaReport(list_problem=[issue for issue in self.list_problem if predicate(issue)],
                            version=self.version)

    @staticmethod
    def from_file(json_path: Union[Path, str]) -> 'QodanaReport':
        return QodanaReport.from_dict(parse_json(json_path))
