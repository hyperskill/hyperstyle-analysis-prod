from dataclasses import dataclass, field
from enum import unique, Enum
from typing import Optional

from dataclasses_json import dataclass_json


@unique
class TestDataField(Enum):
    CLASS_NAME = 'class_name'
    TEST = 'test'
    METHOD_NAME = 'method_name'
    DURATION = 'duration'
    RESULT = 'result'
    TEST_NUMBER = 'test_number'
    ERROR_CLASS = 'error_class'
    MESSAGE = 'message'


class TestResult(Enum):
    PASSED = 'passed'
    FAILED = 'failed'
    IGNORED = 'ignored'


@dataclass_json
@dataclass(frozen=True)
class TestData:
    class_name: str
    test: str
    method_name: str
    duration: str = field(compare=False)
    result: TestResult

    test_number: Optional[int] = None

    error_class: Optional[str] = None
    message: Optional[str] = None

    # TODO: replace similar code
    @property
    def full_test_name(self) -> str:
        base_name = f'{self.class_name}.{self.method_name}'
        if self.test_number is not None:
            base_name += f'[{self.test_number}]'
        return base_name


@dataclass_json
@dataclass
class ExceptionData:
    path: str
    line_number: int
    column_number: int
    message: str
