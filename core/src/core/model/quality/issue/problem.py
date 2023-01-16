from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json, LetterCase

from core.model.quality.issue.issue import BaseIssue


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True, eq=True)
class Code:
    start_line: int
    length: int
    offset: int
    surrounding_code: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True, eq=True)
class Source:
    type: str
    path: str
    language: str
    line: int
    offset: int
    length: int
    code: Code


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True, eq=True)
class Attributes:
    inspection_name: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True, eq=True)
class Problem(BaseIssue):
    tool: str
    category: str
    type: str
    severity: str
    comment: str
    details_info: str
    sources: List[Source]
    attributes: Attributes

    def get_name(self) -> str:
        return self.attributes.inspection_name

    def get_text(self) -> str:
        return self.comment

    def get_line_number(self) -> int:
        return self.sources[0].line

    def get_column_number(self) -> int:
        return self.sources[0].offset

    def get_category(self) -> str:
        return self.category

    def get_difficulty(self) -> str:
        return self.severity
