from dataclasses_json import dataclass_json
from typing import Optional

from dataclasses import dataclass, field

from enum import unique, Enum


@unique
class TestDataField(Enum):
    CLASS_NAME = 'class_name'
    TEST = 'test'
    METHOD_NAME = 'method_name'
    DURATION = 'duration'
    RESULT = 'result'
    ERROR_CLASS = 'error_class'
    MESSAGE = 'message'


@dataclass_json
@dataclass
class TestData:
    class_name: str
    test: str
    method_name: str
    duration: str = field(compare=False)
    result: str

    error_class: Optional[str] = None
    message: Optional[str] = None


@dataclass_json
@dataclass
class ExceptionData:
    path: str
    line_number: int
    column_number: int
    message: str
