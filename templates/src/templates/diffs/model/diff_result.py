from dataclasses import dataclass

from src.templates.diffs.model.diff_interval import DiffInterval
from src.templates.diffs.model.diff_tag import DiffTag


@dataclass(frozen=True)
class DiffResult:
    """
        tag - type of change where 0 (code not changed), 1 (code added), -1 (code deleted)
        patch - part of code which was changes
        template_interval - changed interval in template
        code_interval - changed interval in code
    """
    tag: DiffTag
    patch: str
    template_interval: DiffInterval
    code_interval: DiffInterval
