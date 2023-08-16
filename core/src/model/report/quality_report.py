import json
from dataclasses import dataclass

from dataclasses_json import dataclass_json

from core.src.model.quality.quality import Quality


@dataclass_json
@dataclass(frozen=True, eq=True)
class QualityReport:
    quality: Quality

    def to_str(self) -> str:
        return json.dumps(self.to_dict())