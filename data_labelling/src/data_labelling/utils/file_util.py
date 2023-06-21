from pathlib import Path

from hyperstyle.src.python.review.application_config import LanguageVersion
import pandas as pd

from core.utils.file.file_utils import get_parent_folder
from core.utils.file.saving_utils import save_solution_to_file


def get_solution_id_by_file_path(solution_file_path: str) -> int:
    """
    As solution is store like input_path / root_path / solution_{solution_id} / filename.extension
    we can easily parse solution id from file_path.
    """

    parent_directory = get_parent_folder(solution_file_path)
    _, solution_id = parent_directory.name.split('_')
    return int(solution_id)


def save_solutions_to_files(df_solutions: pd.DataFrame,
                            language_version: LanguageVersion,
                            input_path: Path,
                            with_template: bool = False):
    """
    Save solutions to input_path.
    """
    df_solutions.apply(save_solution_to_file,
                       input_path=input_path,
                       axis=1)
