import os
import sys
from pathlib import Path

from core.src.utils.subprocess_runner import run_in_subprocess
from jba.src import MAIN_FOLDER

from jba.tests.processing import PROCESSING_FOLDER

import tempfile

import yaml

from deepdiff import DeepDiff  # noqa: SC200


def test_incorrect_arguments():
    command = [sys.executable, (MAIN_FOLDER.parent / 'processing' / 'tasktracker_content_collector.py')]

    stdout, stderr = run_in_subprocess(command)

    assert stdout == ''
    assert 'error: the following arguments are required' in stderr


def yaml_as_dict(my_file):
    result = {}
    with open(my_file, 'r') as file_path:
        docs = yaml.safe_load_all(file_path)
        for doc in docs:
            for key, value in doc.items():
                result[key] = value
    return result


def _test_course(course_name):
    with tempfile.TemporaryDirectory() as temp_directory:
        prepare_course_directory = PROCESSING_FOLDER / 'collect_course_structure'
        command = [sys.executable, (MAIN_FOLDER.parent / 'processing' / 'tasktracker_content_collector.py'),
                   Path(temp_directory),
                   prepare_course_directory / course_name]
        stdout, stderr = run_in_subprocess(command)
        assert stdout == ''
        assert stderr == ''
        assert len(os.listdir(temp_directory)) == 1
        file = Path(temp_directory) / 'task_content_default.yaml'
        assert file.exists()
        expected_file = (PROCESSING_FOLDER / 'tasktracker_content_collector' / f'expected_{course_name}.yaml')
        difference = DeepDiff(yaml_as_dict(file), yaml_as_dict(expected_file), ignore_order=True)
        assert not difference


def test_correct_arguments():
    _test_course('course_with_section')
    _test_course('course_without_section')
    _test_course('course_with_undefined_structure_type')
