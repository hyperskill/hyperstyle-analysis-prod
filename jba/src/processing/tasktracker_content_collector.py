import re
from os import listdir

import argparse
from pathlib import Path

import yaml
from core.src.utils.file.extension_utils import AnalysisExtension
from core.src.utils.file.yaml_utils import read_yaml_field_content
from jba.src.models.edu_structure import EduStructureType, EduLesson

CONTENT_META_FIELD = 'content'
FILES_META_FIELD = 'files'
VISIBLE_META_FIELD = 'visible'
TYPE_META_FIELD = 'type'
NAME_META_FIELD = 'name'

CONTENT_FILE_NAME = 'task_content_default.yaml'

FRAMEWORK_TYPE = 'framework'

TASK_DIRECTORY_NAME = 'task'

INFO_FILE_REGEX = re.compile(f'([a-z]+)-info{AnalysisExtension.YAML.value}')

EXTENSIONS = {'py': 'PYTHON', 'ipynb': 'JUPYTER', 'java': 'JAVA', 'kt': 'KOTLIN', 'cpp': 'CPP', 'csv': 'CSV'}


class TaskTrackerFile:
    def __init__(self, rel_path):
        self.path = rel_path.parent
        self.name = rel_path.stem
        self.extension = EXTENSIONS.get(rel_path.suffix.lstrip('.'), 'NOEXTENSION')

    def as_dict(self):
        return {
            'filename': self.name,
            'relativePath': str(self.path),
            'extension': self.extension,
            'sourceSet': 'SRC',
            'isInternal': False
        }


def get_data_template(files: list) -> dict:
    return {
        'tasks': {
            'name': 'example',
            'description': 'description',
            'id': 'main',
            'files': files
        }
    }


def flatten(paths: list) -> list:
    result = []
    for i in paths:
        if i is None:
            continue
        if isinstance(i, list):
            result.extend(flatten(i))
        else:
            result.append(i)
    return result


def get_info_file(root: Path) -> str:
    file_names = listdir(root)
    info_files = list(filter(lambda file_name: re.match(INFO_FILE_REGEX, file_name), file_names))
    info_file = info_files[0]
    return info_file


def get_lessons(root: Path):
    info_file = get_info_file(root)
    info_file_structure_type = re.match(INFO_FILE_REGEX, info_file).group(1)
    structure_type = EduStructureType(info_file_structure_type)
    if structure_type == EduStructureType.LESSON:
        content = read_yaml_field_content(root / info_file, CONTENT_META_FIELD)
        t1 = read_yaml_field_content(root / info_file, TYPE_META_FIELD)
        return EduLesson(root, t1 is not None and t1 == FRAMEWORK_TYPE, content)
    elif structure_type == EduStructureType.TASK or structure_type is None:
        return None
    else:
        children = None
        content = read_yaml_field_content(root / info_file, CONTENT_META_FIELD)
        if content is not None:
            children = flatten([get_lessons(root / name) for name in content])
        return children


def get_files(root: Path, lesson: EduLesson) -> list:
    relative_path = lesson.root.relative_to(root)
    return flatten(
        [get_task_files(lesson.root / child, relative_path, lesson.is_framework) for child in lesson.children])


def get_task_files(root: Path, relative_path: Path, is_framework: bool):
    info_file = get_info_file(root)

    files = read_yaml_field_content(root / info_file, FILES_META_FIELD)
    if files is None:
        files = []
    files = list(filter(lambda file: file[VISIBLE_META_FIELD], files))

    def get_filename(file_content: dict) -> TaskTrackerFile:
        if is_framework:
            return TaskTrackerFile(relative_path / TASK_DIRECTORY_NAME / file_content[NAME_META_FIELD])
        else:
            return TaskTrackerFile(relative_path / root.name / file_content[NAME_META_FIELD])

    return list(map(get_filename, files))


def get_yaml_content(course_root: Path) -> dict:
    lessons = get_lessons(course_root)

    files = set()
    for lesson in lessons:
        for i in get_files(course_root, lesson):
            files.add(i)

    data = get_data_template(list(map(lambda obj: obj.as_dict(), files)))

    return data


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        'destination_path',
        type=lambda value: Path(value).absolute(),
        help='Path to directory where yaml file will be created',
    )

    parser.add_argument(
        'course_sources_path',
        type=lambda value: Path(value).absolute(),
        help='Path to course sources to extract course structure.',
    )


def save_yaml_file(yaml_content: dict, path: Path):
    with open(path, 'w') as file:
        yaml.dump(yaml_content, file)


def main():
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args()

    yaml_content = get_yaml_content(args.course_sources_path)
    save_yaml_file(yaml_content, args.destination_path / CONTENT_FILE_NAME)


if __name__ == '__main__':
    main()
