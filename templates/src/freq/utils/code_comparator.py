from typing import Callable, Optional, Union

from templates.src.freq.utils.code_compare_utils import remove_trailing_comment, remove_trailing_whitespaces, EQUAL


class CodeComparator:
    """ Special comparator to preprocess code lines and compare them. """

    preprocess: Callable[[str], str]
    is_equal: Callable[[str, str], bool]
    is_empty: Callable[[str], bool]

    def __init__(self, equal_type: str,
                 ignore_trailing_comments: bool,
                 ignore_trailing_whitespaces: bool,
                 equal_upper_bound: Optional[Union[int, float]] = None):
        self.preprocess = self._configure_preprocess_code_line(ignore_trailing_comments, ignore_trailing_whitespaces)
        self.is_equal = self._configure_is_equal(equal_type, self.preprocess, equal_upper_bound)
        self.is_empty = self._configure_is_empty(self.preprocess)

    @staticmethod
    def _configure_preprocess_code_line(ignore_trailing_comments: bool = True,
                                        ignore_trailing_whitespaces: bool = True) -> Callable[[str], str]:
        def preprocess(code_line: str) -> str:
            if ignore_trailing_comments:
                code_line = remove_trailing_comment(code_line)
            if ignore_trailing_whitespaces:
                code_line = remove_trailing_whitespaces(code_line)

            return code_line

        return preprocess

    @staticmethod
    def _configure_is_empty(preprocess: Callable[[str], str]) -> Callable[[str], bool]:
        def is_empty(code_line: str) -> bool:
            if preprocess is not None:
                code_line = preprocess(code_line)

            return len(code_line) == 0

        return is_empty

    @staticmethod
    def _configure_is_equal(equal_type: str, preprocess: Callable[[str], str],
                            equal_upper_bound: Optional[Union[int, float]]) -> Callable[[str, str], bool]:
        def is_equal(code_line: str, template_line: str) -> bool:
            if preprocess is not None:
                code_line, template_line = preprocess(code_line), preprocess(template_line)

            equal = EQUAL[equal_type]
            if equal_upper_bound is not None:
                return equal(code_line, template_line, upper_bound=equal_upper_bound)
            return equal(code_line, template_line)

        return is_equal
