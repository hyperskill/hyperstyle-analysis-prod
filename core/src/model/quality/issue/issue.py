from abc import abstractmethod
from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(frozen=True)
class BaseIssue:
    """ All code quality issues which a going to be analyzed should implement this abstract class. """

    @abstractmethod
    def get_name(self) -> str:
        """ Reruns issue name (e.x. MissingBreakInSwitch). """
        pass

    @abstractmethod
    def get_text(self) -> str:
        """ Reruns issue text description (e.x. Break in switch is missed). """
        pass

    @abstractmethod
    def get_line_number(self) -> int:
        """ Reruns line number where issue appeared (starting from 1). """
        pass

    @abstractmethod
    def get_column_number(self) -> int:
        """ Reruns column number where issue appeared (starting from 1). """
        pass

    @abstractmethod
    def get_category(self) -> str:
        """ Reruns issue category (e.x. ERROR_PRONE). """
        pass

    @abstractmethod
    def get_difficulty(self) -> str:
        """ Reruns issue difficulty (e.x. HARD). """
        pass

    def __eq__(self, other):
        # This condition justifiably contains many logical operators
        return self.get_name() == other.get_name() and \
               self.get_text() == other.get_text() and \
               self.get_line_number() == other.get_line_number() and \
               self.get_column_number() == other.get_column_number() and \
               self.get_category() == other.get_category() and \
               self.get_difficulty() == other.get_difficulty()  # noqa: WPS222
