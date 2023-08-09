from core.src.utils.file.file_utils import get_parent_folder


def get_solution_id_by_file_path(solution_file_path: str) -> int:
    """
    As solution is store like input_path / root_path / solution_{solution_id} / filename.extension
    we can easily parse solution id from file_path.
    """

    parent_directory = get_parent_folder(solution_file_path)
    _, solution_id = parent_directory.name.split('_')
    return int(solution_id)
