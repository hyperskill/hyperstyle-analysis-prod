import re
from os import listdir

import argparse
from pathlib import Path

import pandas as pd

from core.src.utils.df_utils import read_df, filter_df_by_single_value, write_df
from core.src.utils.file.extension_utils import AnalysisExtension
from core.src.utils.file.yaml_utils import read_yaml_field_content
from jba.src.models.edu_columns import (
    EduColumnName,
    NUMBER_COLUMN_POSTFIX,
    AMOUNT_COLUMN_POSTFIX,
    ID_COLUMN_POSTFIX,
    NAME_COLUMN_POSTFIX,
)
from jba.src.models.edu_structure import EduStructureNode, EduStructureType

CONTENT_META_FIELD = 'content'
ID_META_FIELD = 'id'

INFO_FILE_REGEX = re.compile(f'([a-z]+)-info{AnalysisExtension.YAML.value}')
REMOTE_INFO_FILE_REGEX = re.compile(f'([a-z]+)-remote-info{AnalysisExtension.YAML.value}')


def _gather_structure(root: Path) -> EduStructureNode:  # noqa: WPS238
    file_names = listdir(root)

    info_files = list(filter(lambda file_name: re.match(INFO_FILE_REGEX, file_name), file_names))
    if len(info_files) != 1:
        raise ValueError(f'The number of info files in {root} must be exactly 1 (actual: {len(info_files)}).')

    info_file = info_files[0]
    info_file_structure_type = re.match(INFO_FILE_REGEX, info_file).group(1)

    remote_info_files = list(filter(lambda file_name: re.match(REMOTE_INFO_FILE_REGEX, file_name), file_names))
    if len(remote_info_files) != 1:
        raise ValueError(
            f'The number of remote info files in {root} must be exactly 1 (actual: {len(remote_info_files)}).',
        )

    remote_info_file = remote_info_files[0]
    remote_info_file_structure_type = re.match(REMOTE_INFO_FILE_REGEX, remote_info_file).group(1)

    if info_file_structure_type != remote_info_file_structure_type:
        raise ValueError(f'Unable to determine a structure type for {root}.')

    structure_type = EduStructureType(info_file_structure_type)

    structure_id = read_yaml_field_content(root / remote_info_file, ID_META_FIELD)
    if structure_id is None:
        raise ValueError(f'{root / remote_info_file} must contain the {ID_META_FIELD} field.')

    children = None
    content = read_yaml_field_content(root / info_file, CONTENT_META_FIELD)
    if content is not None:
        children = [_gather_structure(root / name) for name in content]

        if not all([node.structure_type == children[0].structure_type for node in children]):
            raise ValueError(f'All children nodes inside {root} must have the same structure type.')

    return EduStructureNode(structure_id, root.name, structure_type, children)


def _convert_structure_to_dataframe(structure: EduStructureNode) -> pd.DataFrame:
    if structure.children is None:
        # If node has no content, then it is a task node
        return pd.DataFrame.from_dict(
            {f'{EduColumnName.TASK_ID.value}': [structure.id], f'{EduColumnName.TASK_NAME.value}': [structure.name]}
        )

    children_dfs = []
    for i, node in enumerate(structure.children, start=1):
        node_df = _convert_structure_to_dataframe(node)
        node_df[f'{node.structure_type.value}_{NUMBER_COLUMN_POSTFIX}'] = i
        node_df[f'{node.structure_type.value}_{AMOUNT_COLUMN_POSTFIX}'] = len(structure.children)
        children_dfs.append(node_df)

    structure_df = pd.concat(children_dfs, ignore_index=True)
    structure_df[f'{structure.structure_type.value}_{ID_COLUMN_POSTFIX}'] = structure.id
    structure_df[f'{structure.structure_type.value}_{NAME_COLUMN_POSTFIX}'] = structure.name

    return structure_df


def get_course_structure(course_root: Path) -> pd.DataFrame:
    course_structure = _gather_structure(course_root)
    course_structure_df = _convert_structure_to_dataframe(course_structure)

    # Removing unnecessary column
    course_structure_df.drop(
        columns=[f'{EduStructureType.COURSE.value}_{NAME_COLUMN_POSTFIX}', EduColumnName.COURSE_ID.value],
        inplace=True,
    )

    # Adding the "task global number" column
    course_structure_df.index += 1
    course_structure_df.reset_index(inplace=True, names=[EduColumnName.TASK_GLOBAL_NUMBER.value])

    return course_structure_df


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        'course_sources_path',
        type=lambda value: Path(value).absolute(),
        help='Path to course sources to extract course structure.',
    )

    parser.add_argument(
        'output_path',
        type=lambda value: Path(value).absolute(),
        help='Path to .csv file where to save the course structure.',
    )


def main():
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args()

    course_structure = get_course_structure(args.course_sources_path)
    write_df(course_structure, args.output_path)


if __name__ == '__main__':
    main()
