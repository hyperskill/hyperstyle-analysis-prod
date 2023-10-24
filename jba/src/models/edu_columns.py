from enum import Enum, unique

from jba.src.models.edu_structure import EduStructureType

ID_COLUMN_POSTFIX = 'id'
NAME_COLUMN_POSTFIX = 'name'
NUMBER_COLUMN_POSTFIX = 'number'
AMOUNT_COLUMN_POSTFIX = 'amount'


@unique
class EduColumnName(Enum):
    ID = 'id'
    COURSE_ID = 'course_id'
    SUBMISSION_DATETIME = 'submission_datetime'
    STATUS = 'status'
    USER_ID = 'user_id'
    TASK_TYPE = 'task_type'
    CODE_SNIPPETS = 'code_snippets'
    UUID = 'uuid'

    TASK_GLOBAL_NUMBER = f'{EduStructureType.TASK.value}_global_number'
    TASK_ID = f'{EduStructureType.TASK.value}_{ID_COLUMN_POSTFIX}'
    TASK_NAME = f'{EduStructureType.TASK.value}_{NAME_COLUMN_POSTFIX}'
    TASK_NUMBER = f'{EduStructureType.TASK.value}_{NUMBER_COLUMN_POSTFIX}'
    TASK_AMOUNT = f'{EduStructureType.TASK.value}_{AMOUNT_COLUMN_POSTFIX}'

    LESSON_ID = f'{EduStructureType.LESSON.value}_{ID_COLUMN_POSTFIX}'
    LESSON_NAME = f'{EduStructureType.LESSON.value}_{NAME_COLUMN_POSTFIX}'
    LESSON_NUMBER = f'{EduStructureType.LESSON.value}_{NUMBER_COLUMN_POSTFIX}'
    LESSON_AMOUNT = f'{EduStructureType.LESSON.value}_{AMOUNT_COLUMN_POSTFIX}'

    SECTION_ID = f'{EduStructureType.SECTION.value}_{ID_COLUMN_POSTFIX}'
    SECTION_NAME = f'{EduStructureType.SECTION.value}_{NAME_COLUMN_POSTFIX}'
    SECTION_NUMBER = f'{EduStructureType.SECTION.value}_{NUMBER_COLUMN_POSTFIX}'
    SECTION_AMOUNT = f'{EduStructureType.SECTION.value}_{AMOUNT_COLUMN_POSTFIX}'

    SOLUTION_AWS_KEY = 'solution_aws_key'
    FORMAT_VERSION = 'format_version'
    UPDATE_VERSION = 'update_version'
    CHECKER_OUTPUT = 'checker_output'
    VISIBILITY = 'visibility'

    EXCEPTIONS = 'exceptions'
    TESTS = 'tests'
    INSPECTIONS = 'inspections'


@unique
class EduTaskStatus(Enum):
    WRONG = 'wrong'
    CORRECT = 'correct'


@unique
class EduTaskType(Enum):
    THEORY = 'theory'
    EDU = 'edu'
    UNDEFINED = 'undefined'


@unique
class EduCodeSnippetField(Enum):
    NAME = 'name'
    TEXT = 'text'


@unique
class EduConfigField(Enum):
    TYPE = 'type'
    FILES = 'files'
    CUSTOM_NAME = 'custom_name'
    FEEDBACK_LINK = 'feedback_link'
    NAME = 'name'
    VISIBLE = 'visible'
