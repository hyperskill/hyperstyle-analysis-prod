from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class EduStructureType(Enum):
    COURSE = 'course'
    SECTION = 'section'
    LESSON = 'lesson'
    TASK = 'task'


@dataclass(frozen=True)
class EduStructureNode:
    id: int
    name: str
    structure_type: EduStructureType
    children: Optional[List['EduStructureNode']]
