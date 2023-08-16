import argparse
from os.path import exists
from pathlib import Path
from typing import Any

import pandas as pd
import sys

from core.src.utils.df_utils import read_df, filter_df_by_single_value, write_df
from core.src.utils.file.extension_utils import AnalysisExtension
from core.src.utils.file.file_utils import get_parent_folder, remove_slash
from core.src.utils.file.yaml_utils import parse_yaml
from jba.src.models.edu_columns import EduColumnName
from jba.src.models.edu_config_item import EduConfigItem

CONTENT_FIELD = 'content'
ID_FIELD = 'id'


def parse_course_config(base_path: str, inner_folder: str) -> dict:
    full_path = f'{base_path}/{inner_folder}'
    if not exists(full_path):
        raise ValueError(f'The {inner_folder} does not exist in {base_path}!')
    return parse_yaml(full_path)


def _parse_yaml_section(yaml_config_parsed: dict, yaml_section: str, file_path: str) -> Any:
    if yaml_section not in yaml_config_parsed:
        raise ValueError(f'You need to specify {yaml_section} section in the {file_path} file!')
    return yaml_config_parsed[yaml_section]


def _parse_edu_config_item(base_path: str, nested_folder_name: str, item_type: str,
                           is_terminal: bool = False) -> EduConfigItem:
    current_path = f'{base_path}/{nested_folder_name}'

    item_remote_info_file_name = f'{item_type}-remote-info{AnalysisExtension.YAML.value}'
    item_remote_info_parsed = parse_course_config(current_path, item_remote_info_file_name)
    item_id = _parse_yaml_section(item_remote_info_parsed, ID_FIELD,
                                  f'{current_path}/{item_remote_info_file_name}')

    if not is_terminal:
        item_info_file_name = f'{item_type}-info{AnalysisExtension.YAML.value}'
        item_info_parsed = parse_course_config(current_path, item_info_file_name)
        nested_items = _parse_yaml_section(item_info_parsed, CONTENT_FIELD,
                                           f'{current_path}/{item_info_file_name}')
    else:
        nested_items = None
    return EduConfigItem(item_id, nested_folder_name, item_type, nested_items)


def filter_by_course_id_and_save(df_path: str, course_id: int) -> Path:
    initial_df = read_df(df_path)
    filtered_df = filter_df_by_single_value(initial_df, EduColumnName.COURSE_ID.value, course_id)
    output_folder = get_parent_folder(df_path, to_add_slash=True)
    new_path = f'{output_folder}/course_{course_id}{AnalysisExtension.CSV.value}'
    write_df(filtered_df, new_path)
    return output_folder


def _gather_course_structure(course_root_path: str) -> pd.DataFrame:
    course_info_file_name = f'course-info{AnalysisExtension.YAML.value}'
    course_root_path_without_slash = remove_slash(course_root_path)
    course_info_parsed = parse_course_config(course_root_path_without_slash, course_info_file_name)
    sections = _parse_yaml_section(course_info_parsed, CONTENT_FIELD, course_root_path_without_slash)
    headers = [
        EduColumnName.TASK_GLOBAL_NUMBER.value,
        EduColumnName.TASK_ID.value, EduColumnName.TASK_NAME.value, EduColumnName.TASK_NUMBER.value,
        EduColumnName.TASKS_AMOUNT.value,
        EduColumnName.LESSON_ID.value, EduColumnName.LESSON_NAME.value, EduColumnName.LESSON_NUMBER.value,
        EduColumnName.LESSONS_AMOUNT.value,
        EduColumnName.SECTION_ID.value, EduColumnName.SECTION_NAME.value, EduColumnName.SECTION_NUMBER.value,
        EduColumnName.SECTIONS_AMOUNT.value,
    ]
    rows = []
    sections_amount = len(sections)
    task_global_number = 0
    for i, section in enumerate(sections):
        section_parsed = _parse_edu_config_item(course_root_path_without_slash, section, 'section')
        current_section_path = f'{course_root_path_without_slash}/{section}'
        lessons_amount = len(section_parsed.nested_items)
        for j, lesson in enumerate(section_parsed.nested_items):
            lesson_parsed = _parse_edu_config_item(current_section_path, lesson, 'lesson')
            current_lesson_path = f'{current_section_path}/{lesson}'
            tasks_amount = len(lesson_parsed.nested_items)
            for k, task in enumerate(lesson_parsed.nested_items):
                task_parsed = _parse_edu_config_item(current_lesson_path, task, 'task', True)
                # task_global_number
                # task_id, task_name, task_number, tasks_amount,
                # lesson_id, lesson_name, lesson_number, lessons_amount,
                # section_id, section_name, section_number, sections_amount
                task_global_number += 1
                rows.append([
                    task_global_number,
                    task_parsed.id, task_parsed.name, k + 1, tasks_amount,
                    lesson_parsed.id, lesson_parsed.name, j + 1, lessons_amount,
                    section_parsed.id, section_parsed.name, i + 1, sections_amount
                ])
    return pd.DataFrame(rows, columns=headers)


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('data_path', type=str, help='Path to .csv file with collected data.')
    parser.add_argument('course_id', type=int, help='Course id to analyze.')
    parser.add_argument('course_sources_path', type=str, help='Path to course sources to extract course structure.')


def main():
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args(sys.argv[1:])
    output_path = filter_by_course_id_and_save(args.data_path, args.course_id)
    tasks_info_df = _gather_course_structure(args.course_sources_path)
    write_df(tasks_info_df, f'{output_path}/course_{args.course_id}_structure{AnalysisExtension.CSV.value}')


if __name__ == '__main__':
    main()
