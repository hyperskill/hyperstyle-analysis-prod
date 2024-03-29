from enum import Enum, unique


@unique
class ObjectClass(str, Enum):  # noqa: WPS600 We can inherit from str in Enums
    SEARCH_RESULT = 'search-result'
    LESSON = 'lesson'
    COURSE = 'course'
    STEP = 'step'
    USER = 'user'
    SUBMISSION = 'submission'

    @classmethod
    def values(cls):
        return list(map(lambda c: c.value, cls))


class StepikPlatform:
    BASE_URL = 'https://stepik.org'
    CLIENT_ID = 'STEPIK_CLIENT_ID'
    CLIENT_SECRET = 'STEPIK_CLIENT_SECRET'
