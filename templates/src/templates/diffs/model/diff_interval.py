from dataclasses import dataclass


@dataclass(frozen=True)
class DiffInterval:
    """
        start - position of change start (included)
        end - position of change end (excluded)
    """
    start: int
    end: int
