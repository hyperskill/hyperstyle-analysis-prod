from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(frozen=True, eq=True)
class Quality:
    code: str
    text: str
