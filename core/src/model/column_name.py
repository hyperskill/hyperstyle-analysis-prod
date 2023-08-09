from enum import Enum, unique


@unique
class StepColumns(Enum):
    ID = 'id'
    COMMENTS = 'comments_statistics'
    LIKES = 'likes_statistics'
    STEPIC_LESSON_ID = 'lesson_stepik_id'
    POSITION = 'position'
    SECONDS_TO_COMPLETE = 'seconds_to_complete'
    SOLVED_BY = 'solved_by'
    STAGE = 'stage'
    STEPIK_ID = 'stepik_id'
    SUCCESS_RATE = 'success_rate'
    TOPIC = 'topic'
    TOPIC_ID = 'topic_id'
    TOPIC_THEORY = 'topic_theory'
    TYPE = 'type'
    TITLE = 'title'
    POPULAR_IDE = 'popular_ide'
    PROJECT = 'project'
    IS_IDE_COMPATIBLE = 'is_ide_compatible'
    OPTIONS = 'options'
    DEPTH = 'depth'
    PREREQUISITES_COUNT = 'prerequisites_count'
    URL = 'url'

    BLOCK = 'block'
    TEXT = 'text'
    LANGUAGE = 'language'

    HEADER_LINES_COUNT = 'code_templates_header_lines_count'
    FOOTER_LINES_COUNT = 'code_templates_footer_lines_count'
    CODE_TEMPLATES = 'code_templates'
    CODE_TEMPLATE = 'code_template'
    HAS_HEADER_FOOTER = 'has_header_footer'
    HAS_TEMPLATE = 'has_template'
    HAS_CONSTANT = 'has_constant'

    COMPLEXITY = 'complexity'
    DIFFICULTY = 'difficulty'
    SCOPE = 'scope'

    VALUE = 'value'
    TOTAL_COUNT = 'total_count'

    THREAD = 'thread'


@unique
class SubmissionColumns(Enum):
    ID = 'id'
    USER_ID = 'user_id'
    GROUP = 'group'
    ATTEMPT = 'attempt'
    TOTAL_ATTEMPTS = 'total_attempts'
    BASE_CLIENT = 'base_client'
    CLIENT = 'client'
    CLIENT_SERIES = 'client_series'
    STEP = 'step'
    STEP_ID = 'step_id'
    CODE = 'code'
    LANG = 'lang'
    TIME = 'time'
    HIDDEN_CODE_TEMPLATE = 'hidden_code_template'
    CODE_STYLE = 'code_style'
    CODE_STYLE_FEEDBACK_TIME = 'code_style_feedback_time'

    # issues
    RAW_ISSUES = 'raw_issues'
    RAW_ISSUES_ALL = 'raw_issues_all'
    RAW_ISSUES_DIFF = 'raw_issues_diff'
    HYPERSTYLE_ISSUES = 'hyperstyle_issues'
    QODANA_ISSUES = 'qodana_issues'


@unique
class IssuesColumns(Enum):
    NAME = 'name'
    CATEGORY = 'category'
    COUNT = 'count'
    TEXT = 'text'
    CODE_SAMPLE = 'code_sample'
    DIFFICULTY = 'difficulty'
    POSITION = 'position'


@unique
class Client(Enum):
    WEB = 'web'
    IDEA = 'idea'


@unique
class CommentsColumns(Enum):
    COMMENT = 'comment'
    HINT = 'hint'
    USEFUL_LINK = 'useful link'
    SOLUTIONS = 'solutions'


@unique
class LikesColumns(Enum):
    LOVE = 'love'
    HAPPY = 'happy'
    NEUTRAL = 'neutral'
    SAD = 'sad'
    ANGRY = 'angry'


@unique
class Complexity(Enum):
    SHALLOW = 'shallow'
    MIDDLE = 'middle'
    DEEP = 'deep'


@unique
class Difficulty(Enum):
    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'


@unique
class Scope(Enum):
    SMALL = 'small'
    MEDIUM = 'medium'
    WIDE = 'wide'


@unique
class TopicColumns(Enum):
    ID = 'id'
    CHILDREN = 'children'
    DEPTH = 'depth'
    PREREQUISITES_COUNT = 'prerequisites_count'
    HIERARCHY = 'hierarchy'
    PREREQUISITES = 'prerequisites'
    ROOT_ID = 'root_id'
    ROOT_TITLE = 'root_title'
    TITLE = 'title'
    TOPOLOGICAL_INDEX = 'topological_index'
    THEORY = 'theory'
    PARENT_ID = 'parent_id'
    HAS_STEPS = 'has_steps'
    URL = 'url'
