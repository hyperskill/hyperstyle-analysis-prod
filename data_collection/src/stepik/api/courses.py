"""
This file contains classes, which describe course entity from Stepik platform. Course is a group of lessons.
Courses are available by API requests, described at
    https://stepic.org/api/docs/#!/courses
"""

from dataclasses import dataclass, field
from typing import List, Optional

from core.src.model.api.platform_objects import BaseRequestParams, Object, ObjectResponse
from data_collection.src.stepik.stepik_objects import StepikPlatform


@dataclass
class CourseRequestParams(BaseRequestParams):
    pass


@dataclass(frozen=True)
class Course(Object):
    id: int
    summary: str
    workload: str
    intro: str
    course_format: str
    target_audience: str
    certificate_footer: Optional[str]
    certificate_cover_org: Optional[str]
    is_certificate_issued: bool
    is_certificate_auto_issued: bool
    certificate_regular_threshold: Optional[int]
    certificate_distinction_threshold: Optional[int]
    certificates_count: int
    learners_count: int
    lessons_count: int
    quizzes_count: int
    challenges_count: int
    course_type: str
    requirements: str
    description: str
    total_units: int
    videos_duration: int
    time_to_complete: Optional[int]
    language: str

    url: str = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, 'url', f'{StepikPlatform.BASE_URL}/course/{self.id}/promo')  # noqa: WPS609


@dataclass(frozen=True)
class CoursesResponse(ObjectResponse[Course]):
    courses: List[Course]

    def get_objects(self) -> List[Course]:
        return self.courses
