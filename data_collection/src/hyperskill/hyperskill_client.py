import os
from typing import Callable, Dict, List, Optional

from data_collection.src.api.platform_client import PlatformClient
from core.src.model.api.platform_objects import BaseRequestParams, Object
from data_collection.src.hyperskill.api.projects import Project, ProjectsResponse
from data_collection.src.hyperskill.api.search_results import \
    SearchResult, SearchResultsRequestParams, SearchResultsResponse
from data_collection.src.hyperskill.api.steps import StepsRequestParams, StepsResponse
from data_collection.src.hyperskill.api.submissions import Submission, SubmissionRequestParams, SubmissionResponse
from data_collection.src.hyperskill.api.topics import Topic, TopicsResponse
from data_collection.src.hyperskill.api.tracks import Track, TracksResponse
from data_collection.src.hyperskill.api.users import User, UserResponse
from data_collection.src.hyperskill.hyperskill_objects import HyperskillPlatform, ObjectClass


ObjectRequestor = Callable[[Optional[List[int]], Optional[int]], List[Object]]


class HyperskillClient(PlatformClient):
    """
    Client for Hyperskill educational platform which allows to get information about
    steps, topics, projects, tracks, users, submissions from platform's database. Requires CLIENT_ID and CLIENT_SECRET
    for data exchange.
    """

    def __init__(self, port: int = 8000):
        client_id = os.environ.get(HyperskillPlatform.CLIENT_ID)
        client_secret = os.environ.get(HyperskillPlatform.CLIENT_SECRET)
        super().__init__(HyperskillPlatform.BASE_URL, client_id, client_secret, port)

        self._get_objects_by_class: Dict[ObjectClass, ObjectRequestor] = {
            ObjectClass.TOPIC: self.get_topics,
            ObjectClass.TRACK: self.get_tracks,
            ObjectClass.PROJECT: self.get_projects,
            ObjectClass.USER: self.get_users,
            ObjectClass.STEP: self.get_steps,
            ObjectClass.SUBMISSION: self.get_submissions,
        }

    def get_objects(self, obj: str, ids: Optional[List[int]] = None, count: Optional[int] = None) -> List[Object]:
        if obj not in ObjectClass.values():
            return self.get_search_result(obj, count)

        return self._get_objects_by_class[ObjectClass(obj)](ids, count)

    def get_search_result(self, query: str, count: Optional[int] = None) -> List[SearchResult]:
        """ Returns objects which are best matched the query."""
        return self._get_objects(ObjectClass.SEARCH_RESULT, SearchResultsResponse,
                                 SearchResultsRequestParams(query=query), count=count)

    def get_steps(self, ids: Optional[List[int]] = None,
                  count: Optional[int] = None,
                  topic_ids: Optional[List[int]] = None):
        """ Returns steps data. If topic_ids are defined method returns steps only related to listed topics, otherwise
         return all steps. """
        if topic_ids is None:
            topics = self.get_topics()
            topic_ids = [t.id for t in topics]

        steps = []
        for topic_id in topic_ids:
            steps += self._get_objects(ObjectClass.STEP, StepsResponse,
                                       StepsRequestParams(topic=topic_id), count=count)
            if count is not None and len(steps) >= count:
                return steps[:count]

        if ids is not None:
            steps = [s for s in steps if s.id in ids]

        return steps

    def get_topics(self, ids: Optional[List[int]] = None, count: Optional[int] = None) -> List[Topic]:
        """ Returns topics data. """
        return self._get_objects(ObjectClass.TOPIC, TopicsResponse,
                                 BaseRequestParams(ids=ids), count=count)

    def get_projects(self, ids: Optional[List[int]] = None, count: Optional[int] = None) -> List[Project]:
        """ Returns projects data. """
        return self._get_objects(ObjectClass.PROJECT, ProjectsResponse,
                                 BaseRequestParams(ids=ids), count=count)

    def get_tracks(self, ids: Optional[List[int]] = None, count: Optional[int] = None) -> List[Track]:
        """ Returns tracks data. """
        return self._get_objects(ObjectClass.TRACK, TracksResponse,
                                 BaseRequestParams(ids=ids), count=count)

    def get_users(self, ids: Optional[List[int]] = None, count: Optional[int] = None) -> List[User]:
        """ Returns users data. Only about users which have shared their profile data. """
        return self._get_objects(ObjectClass.USER, UserResponse,
                                 BaseRequestParams(ids=ids), count=count)

    def get_submissions(self, ids: Optional[List[int]] = None,
                        count: Optional[int] = None,
                        step_ids: Optional[List[int]] = None,
                        user_ids: Optional[List[int]] = None) -> List[Submission]:
        """ Returns submissions data. Only for steps, which have been passed by application owner and only submissions
        which were shared by user. """
        if user_ids is None:
            return self._get_objects(ObjectClass.SUBMISSION, SubmissionResponse,
                                     SubmissionRequestParams(ids=ids, step=step_ids), count=count)

        submissions = []
        for user_id in user_ids:
            submissions += self._get_objects(ObjectClass.SUBMISSION, SubmissionResponse,
                                             SubmissionRequestParams(ids=ids, step=step_ids, user=user_id), count=count)
            if count is not None and len(submissions) >= count:
                return submissions[:count]
        return submissions
