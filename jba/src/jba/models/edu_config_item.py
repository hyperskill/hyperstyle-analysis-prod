from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class EduConfigItem:
    id: int
    name: str
    item_type: str
    nested_items: Optional[List[str]]
