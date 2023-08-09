from dataclasses import dataclass

from dataclasses_json import dataclass_json

from core.src.model.quality.issue.issue import BaseIssue


@dataclass_json
@dataclass(frozen=True)
class HyperstyleIssue(BaseIssue):
    code: str
    text: str
    line: str
    line_number: int
    column_number: int
    category: str
    difficulty: str
    influence_on_penalty: int

    def get_name(self) -> str:
        return self.code

    def get_text(self) -> str:
        return self.text

    def get_line_number(self) -> int:
        return self.line_number

    def get_column_number(self) -> int:
        return self.column_number

    def get_category(self) -> str:
        return self.category

    def get_difficulty(self) -> str:
        return self.difficulty
