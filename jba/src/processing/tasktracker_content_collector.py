import argparse
import itertools
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict

from collect_course_structure import gather_structure
from core.src.utils.file.file_utils import find_files_by_regex
from core.src.utils.file.yaml_utils import read_yaml_field_content, save_as_yaml
from jba.src.models.edu_structure import (
    EduStructureType,
    EduStructureNode,
    EduInfoFileField,
    INFO_FILE_REGEX,
)

CONTENT_FILE_NAME = 'task_content_default.yaml'
FRAMEWORK_TYPE = 'framework'
TASK_DIRECTORY_NAME = 'task'
EXTENSIONS = {'py': 'PYTHON', 'ipynb': 'JUPYTER', 'java': 'JAVA', 'kt': 'KOTLIN', 'cpp': 'CPP', 'csv': 'CSV'}


@dataclass(frozen=True)
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


def get_info_file(root: Path) -> str:
    info_files = find_files_by_regex(root, INFO_FILE_REGEX)
    return info_files[0]


def get_lesson_files(course_root: Path, relative_path: Path, lesson: EduStructureNode) -> List[TaskTrackerFile]:
    lesson_path = course_root / relative_path
    info_file = get_info_file(lesson_path)
    lesson_type = read_yaml_field_content(lesson_path / info_file, EduInfoFileField.TYPE.value)
    return itertools.chain.from_iterable(
        [get_task_files(lesson_path / child.name,
                        relative_path,
                        lesson_type == FRAMEWORK_TYPE)
         for child in lesson.children])


def get_task_files(task_root: Path, relative_path: Path, is_framework: bool) -> List[TaskTrackerFile]:
    info_file = get_info_file(task_root)

    files = read_yaml_field_content(task_root / info_file, EduInfoFileField.FILES.value, [])
    files = list(filter(lambda file: file[EduInfoFileField.VISIBLE.value], files))

    def convert_to_task_tracker_file(file_content: Dict) -> TaskTrackerFile:
        if is_framework:
            return TaskTrackerFile(relative_path / TASK_DIRECTORY_NAME / file_content[EduInfoFileField.NAME.value])
        return TaskTrackerFile(relative_path / task_root.name / file_content[EduInfoFileField.NAME.value])

    return list(map(convert_to_task_tracker_file, files))


def get_yaml_content(course_root: Path) -> Dict:
    course_structure = gather_structure(course_root)
    lessons = course_structure.gather_leafs_of_type(EduStructureType.LESSON)
    files = {
        file
        for path, lesson in lessons.items()
        for file in get_lesson_files(course_root, Path(*path[1:]), lesson)
    }
    return get_data_template(list(map(lambda obj: obj.as_dict(), files)))


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        'course_sources_path',
        type=lambda value: Path(value).absolute(),
        help='Path to course sources to extract course structure.',
    )

    parser.add_argument(
        'destination_path',
        type=lambda value: Path(value).absolute(),
        help='Path to directory where yaml file will be created',
    )


def main():
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args()

    yaml_content = get_yaml_content(args.course_sources_path)
    save_as_yaml(yaml_content, args.destination_path / CONTENT_FILE_NAME)


if __name__ == '__main__':
    main()
