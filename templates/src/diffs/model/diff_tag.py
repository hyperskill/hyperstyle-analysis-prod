from enum import Enum, unique


@unique
class DiffTag(Enum):
    ADDITION = 1
    EQUAL = 0
    DELETION = -1

