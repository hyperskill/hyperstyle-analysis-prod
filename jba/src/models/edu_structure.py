import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Tuple

from core.src.utils.file.extension_utils import AnalysisExtension

INFO_FILE_REGEX = re.compile(f'([a-z]+)-info{AnalysisExtension.YAML.value}')
REMOTE_INFO_FILE_REGEX = re.compile(f'([a-z]+)-remote-info{AnalysisExtension.YAML.value}')


class EduInfoFileField(Enum):
    ID = 'id'
    CONTENT = 'content'
    FILES = 'files'
    VISIBLE = 'visible'
    TYPE = 'type'
    NAME = 'name'


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

    def gather_leafs_of_type(self, leaf_type: EduStructureType) -> Dict[Tuple[str], 'EduStructureNode']:
        if self.structure_type == leaf_type:
            return {(self.name,): self}

        if self.children is None:
            return {}

        return {
            (self.name, *path): leaf
            for child in self.children
            for path, leaf in child.gather_leafs_of_type(leaf_type).items()
        }
