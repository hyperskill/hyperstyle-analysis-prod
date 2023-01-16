from enum import Enum, unique


@unique
class DiffType(Enum):
    CLEAN_SEMANTIC = 0
    CLEAN_EFFICIENCY = 1
    LEVENSHTEIN = -1

