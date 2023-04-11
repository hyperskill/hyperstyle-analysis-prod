import os
from pathlib import Path
from typing import Union

import pandas as pd

from core.model.column_name import SubmissionColumns
from core.utils.file.file_utils import create_file
from core.utils.quality.report_utils import get_language_version


def save_solution_to_file(solution: pd.Series,
                          input_path: Path,
                          filename: str = 'code') -> Path:
    """
    Save solution code to file with path: input_path / root_path / solution_{solution_id} / filename.extension where:
    root_path = default_root_path by default but can be changes according to solution language version template
    filename = default_filename by default but can be changes according to solution language version template
    extension is selected according to solution language version

    Examples:
    java11 file with template: input_path/src/main/java/solution_12/Main.java
    java11 file without template: input_path/solution_12/code.java

    python3 file with template: input_path/solution_13/main.py
    python3 file without template: input_path/solution_13/code.py

    js file without template: input_path/solution_14/code.js
    """

    solution_id = solution[SubmissionColumns.ID.value]
    solution_code = solution[SubmissionColumns.CODE.value]
    lang = solution[SubmissionColumns.LANG.value]
    language_version = get_language_version(lang)
    extension = language_version.extension_by_language()

    solution_file_path = input_path / f'solution_{solution_id}' / f'{filename}{extension.value}'

    return save_code_to_file(solution_file_path, solution_code)


def save_code_to_file(file_path: Union[Path, str], code: str) -> Path:
    """ Save solution code to given file_path. """

    solution_file_path = next(create_file(file_path, code))
    os.chmod(solution_file_path, 0o777)
    return solution_file_path
