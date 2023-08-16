import os
from typing import Callable, Dict, List, Optional, Type, TypeVar

from data_collection.src.api.platform_client import PlatformClient
from core.src.model.api.platform_objects import BaseRequestParams, Object, ObjectResponse
from data_collection.src.stepik.api.courses import Course, CoursesResponse
from data_collection.src.stepik.api.lessons import Lesson, LessonsResponse
from data_collection.src.stepik.api.search_results import SearchResult, SearchResultsRequestParams, \
    SearchResultsResponse
from data_collection.src.stepik.api.steps import Step, StepsResponse
from data_collection.src.stepik.api.submissions import Submission, SubmissionsResponse
from data_collection.src.stepik.api.users import User, UsersResponse
from data_collection.src.stepik.stepik_objects import ObjectClass, StepikPlatform

T = TypeVar('T', bound=Object)
ObjectRequestor = Callable[[Optional[List[int]], Optional[int]], List[Object]]


class StepikClient(PlatformClient):

    def __init__(self, port: int = 8000):
        client_id = os.environ.get(StepikPlatform.CLIENT_ID)
        client_secret = os.environ.get(StepikPlatform.CLIENT_SECRET)
        super().__init__(StepikPlatform.BASE_URL, client_id, client_secret, port)

        self._get_objects_by_class: Dict[ObjectClass, ObjectRequestor] = {
            ObjectClass.COURSE: self.get_courses,
            ObjectClass.LESSON: self.get_lessons,
            ObjectClass.STEP: self.get_steps,
            ObjectClass.USER: self.get_users,
            ObjectClass.SUBMISSION: self.get_submissions,
        }

    def get_objects(self, obj: str, ids: Optional[List[int]] = None, count: Optional[int] = None) -> List[Object]:
        if obj not in ObjectClass.values():
            return self.get_search_result(obj, count)

        return self._get_objects_by_class[ObjectClass(obj)](ids, count)

    def get_search_result(self, query: str, count: Optional[int] = None) -> List[SearchResult]:
        return self._get_objects(ObjectClass.SEARCH_RESULT, SearchResultsResponse,
                                 SearchResultsRequestParams(query=query), count=count)

    def get_courses(self, ids: Optional[List[int]] = None, count: Optional[int] = None) -> List[Course]:
        return self._get_objects_default(ids, count, ObjectClass.COURSE, CoursesResponse)

    def get_lessons(self, ids: Optional[List[int]] = None, count: Optional[int] = None) -> List[Lesson]:
        return self._get_objects_default(ids, count, ObjectClass.LESSON, LessonsResponse)

    def get_steps(self, ids: Optional[List[int]] = None, count: Optional[int] = None) -> List[Step]:
        return self._get_objects_default(ids, count, ObjectClass.STEP, StepsResponse)

    def get_users(self, ids: Optional[List[int]] = None, count: Optional[int] = None) -> List[User]:
        return self._get_objects_default(ids, count, ObjectClass.USER, UsersResponse)

    def get_submissions(self, ids: Optional[List[int]] = None, count: Optional[int] = None) -> List[Submission]:
        return self._get_objects_default(ids, count, ObjectClass.SUBMISSION, SubmissionsResponse)

    def _get_objects_default(self,
                             ids: Optional[List[int]],
                             count: Optional[int],
                             obj_class: ObjectClass,
                             obj_response_type: Type[ObjectResponse[T]]) -> List[T]:
        params = BaseRequestParams()
        return self._get_objects_by_ids(obj_class, ids, obj_response_type, params, count=count) if ids is not None \
            else self._get_objects(obj_class, obj_response_type, params, count=count)
