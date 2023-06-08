from enum import Enum, unique


@unique
class EduColumnName(Enum):
    ID = 'id'
    COURSE_ID = 'course_id'
    SUBMISSION_DATETIME = 'submission_datetime'
    STATUS = 'status'
    USER_ID = 'user_id'
    TASK_TYPE = 'task_type'

    TASK_ID = 'task_id'
    TASK_GLOBAL_NUMBER = 'task_global_number'
    TASK_NAME = 'task_name'
    TASK_NUMBER = 'task_number'
    TASKS_AMOUNT = 'tasks_amount'

    LESSON_ID = 'lesson_id'
    LESSON_NAME = 'lesson_name'
    LESSON_NUMBER = 'lesson_number'
    LESSONS_AMOUNT = 'lessons_amount'

    SECTION_ID = 'section_id'
    SECTION_NAME = 'section_name'
    SECTION_NUMBER = 'section_number'
    SECTIONS_AMOUNT = 'sections_amount'


@unique
class EduTaskStatus(Enum):
    WRONG = 'wrong'
    CORRECT = 'correct'


@unique
class EduTaskType(Enum):
    THEORY = 'theory'
    EDU = 'edu'
    UNDEFINED = 'undefined'