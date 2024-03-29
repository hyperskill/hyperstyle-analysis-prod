import re
from math import floor


def edit_distance(first_string: str, second_string: str) -> int:
    """ Compute edit distance for two strings. """

    n = len(first_string) + 1
    m = len(second_string) + 1
    dp = [[0 for _ in range(m)] for _ in range(n)]
    for i in range(1, n):
        dp[i][0] = i
    for j in range(1, m):
        dp[0][j] = j

    for i in range(1, n):
        for j in range(1, m):
            d = 0 if first_string[i - 1] == second_string[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j - 1] + d, dp[i - 1][j] + 1, dp[i][j - 1] + 1)

    return dp[n - 1][m - 1]


def equal_edit_distance(code_line: str, template_line: str, upper_bound: int = 0) -> bool:
    """ Consider two strings as equal if their edit distance is no more than upper_bound. """
    if upper_bound == 0:
        return code_line == template_line
    return edit_distance(code_line, template_line) <= upper_bound


def equal_edit_ratio(code_line: str, template_line: str, upper_bound: float = 0.2) -> bool:
    """ Consider two strings as equal if their edit distance is no more than upper_bound of max of strings length. """
    return equal_edit_distance(code_line, template_line, floor(max(len(code_line), len(template_line)) * upper_bound))


def equal_substring(code_line: str, template_line: str) -> bool:
    """ Consider two lines are equal if template line is substring of code line. """
    return template_line in code_line


SINGLE_TRAILING_PYTHON_COMMENT = re.compile('^(.+)(#.*)$')
DOUBLE_TRAILING_PYTHON_COMMENT = re.compile(r'^(.+)(\"\"\".*\"\"\")$')
SINGLE_TRAILING_JAVA_COMMENT = re.compile('^(.+)(//.*)$')
DOUBLE_TRAILING_JAVA_COMMENT = re.compile(r'^(.+)(/\*.*\*/)$')

COMMENT_REGEX = [SINGLE_TRAILING_PYTHON_COMMENT,
                 DOUBLE_TRAILING_PYTHON_COMMENT,
                 SINGLE_TRAILING_JAVA_COMMENT,
                 DOUBLE_TRAILING_JAVA_COMMENT]


def has_comment(line: str) -> bool:
    """ Check if line has comment. """

    return any(comment_symbol in line for comment_symbol in ['//', '/*', '#', '""""'])


def remove_trailing_comment(line: str) -> str:
    """ Remove trailing comment by regex. """

    for comment_regex in COMMENT_REGEX:
        match = re.match(comment_regex, line)
        line = match[1] if match is not None else line

    return line


def remove_trailing_whitespaces(line: str):
    """ Remove trailing whitespace from line. """

    return line.strip()


EQUAL = {
    'edit_distance': equal_edit_distance,
    'edit_ratio': equal_edit_ratio,
    'substring': equal_substring,
}
