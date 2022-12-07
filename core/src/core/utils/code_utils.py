from typing import List


def split_code_to_lines(code: str, keep_ends: bool = False) -> List[str]:
    """ Split code to lines. Considers both line separations models (with and without \r). """

    return code.splitlines(keep_ends)
