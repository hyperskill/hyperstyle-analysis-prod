from abc import abstractmethod
from dataclasses import dataclass
from typing import Callable, List

from dataclasses_json import dataclass_json

from core.src.model.quality.issue.issue import BaseIssue


@dataclass_json
@dataclass(frozen=True)
class BaseReport:
    """ All code quality reports which a going to be analyzed should implement this abstract class. """

    def has_issue(self, name: str):
        for issue in self.get_issues():
            if issue.get_name() == name:
                return True
        return False

    @abstractmethod
    def get_issues(self) -> List[BaseIssue]:
        """ Returns a list of issues which report contains. """
        pass

    @abstractmethod
    def filter_issues(self, predicate: Callable[[BaseIssue], bool]) -> 'BaseReport':
        """ Leave issues in report which satisfy given `predicate`. """
        pass
