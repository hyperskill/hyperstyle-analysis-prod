import re
from dataclasses import dataclass
from os import listdir

import argparse
from pathlib import Path

from core.src.utils.file.yaml_utils import read_yaml_field_content, save_as_yaml
from jba.src.models.edu_structure import EduStructureType, EduLesson, EduStructureNode
from collect_course_structure import INFO_FILE_REGEX, _gather_structure  # noqa: WPS450
from typing import List, Dict

CONTENT_META_FIELD = 'content'
FILES_META_FIELD = 'files'
VISIBLE_META_FIELD = 'visible'
TYPE_META_FIELD = 'type'
NAME_META_FIELD = 'name'

CONTENT_FILE_NAME = 'task_content_default.yaml'

FRAMEWORK_TYPE = 'framework'

TASK_DIRECTORY_NAME = 'task'

EXTENSIONS = {'py': 'PYTHON', 'ipynb': 'JUPYTER', 'java': 'JAVA', 'kt': 'KOTLIN', 'cpp': 'CPP', 'csv': 'CSV'}


@dataclass(eq=False, frozen=True)
class TaskTrackerFile:
    rel_path: Path

    @property
    def name(self) -> str:
        return self.rel_path.stem

    @property
    def path(self) -> Path:
        return self.rel_path.parent

    @property
    def extension(self) -> str:
        return EXTENSIONS.get(self.rel_path.suffix.lstrip('.'), 'NO_EXTENSION')

    def as_dict(self) -> dict:
        return {
            'filename': self.name,
            'relativePath': str(self.path),
            'extension': self.extension,
            'sourceSet': 'SRC',
            'isInternal': False
        }


def get_data_template(files: List[Dict]) -> Dict:
    return {
        'tasks': [{
            'name': 'example',
            'description': 'description',
            'id': 'main',
            'files': files
        }]
    }


def flatten(files: List) -> List[TaskTrackerFile]:
    result = []
    for i in files:
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

    return info_files[0]


def get_files(root: Path, lesson: EduLesson) -> List[TaskTrackerFile]:
    relative_path = lesson.root.relative_to(root)
    return flatten(
        [get_task_files(lesson.root / child, relative_path, lesson.is_framework) for child in lesson.children])


def get_task_files(root: Path, relative_path: Path, is_framework: bool):
    info_file = get_info_file(root)

    files = read_yaml_field_content(root / info_file, FILES_META_FIELD)
    if files is None:
        files = []
    files = list(filter(lambda file: file[VISIBLE_META_FIELD], files))

    def get_filename(file_content: Dict) -> TaskTrackerFile:
        if is_framework:
            return TaskTrackerFile(relative_path / TASK_DIRECTORY_NAME / file_content[NAME_META_FIELD])
        return TaskTrackerFile(relative_path / root.name / file_content[NAME_META_FIELD])

    return list(map(get_filename, files))


def course_structure_to_lessons(root: Path, structure: EduStructureNode):
    if structure.structure_type == EduStructureType.TASK:
        return None
    if structure.structure_type == EduStructureType.COURSE:
        path = root
    else:
        path = root / structure.name
    if structure.structure_type == EduStructureType.LESSON:
        info_file = get_info_file(path)
        content = read_yaml_field_content(path / info_file, CONTENT_META_FIELD)
        yaml_file_content = read_yaml_field_content(path / info_file, TYPE_META_FIELD)
        return EduLesson(path, yaml_file_content is not None and yaml_file_content == FRAMEWORK_TYPE, content)
    return flatten([course_structure_to_lessons(path, node) for node in structure.children])


def get_yaml_content(course_root: Path) -> Dict:
    course_structure = _gather_structure(course_root)
    lessons = course_structure_to_lessons(course_root, course_structure)

    files = set()
    for lesson in lessons:
        for file in get_files(course_root, lesson):
            files.add(file)
    return get_data_template(list(map(lambda obj: obj.as_dict(), files)))


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


def main():
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args()

    yaml_content = get_yaml_content(args.course_sources_path)
    save_as_yaml(yaml_content, args.destination_path / CONTENT_FILE_NAME)


if __name__ == '__main__':
    main()
