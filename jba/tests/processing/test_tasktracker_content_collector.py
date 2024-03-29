import os
import sys
from pathlib import Path

import pytest

from core.src.utils.file.yaml_utils import parse_yaml
from core.src.utils.subprocess_runner import run_in_subprocess
from jba.src import MAIN_FOLDER

from jba.tests.processing import PROCESSING_FOLDER, COLLECT_COURSE_STRUCTURE_FOLDER

import tempfile

from deepdiff import DeepDiff

TASKTRACKER_CONTENT_COLLECTOR_FOLDER = PROCESSING_FOLDER / 'tasktracker_content_collector'


def test_incorrect_arguments():
    command = [sys.executable, (MAIN_FOLDER.parent / 'processing' / 'tasktracker_content_collector.py')]

    stdout, stderr = run_in_subprocess(command)

    assert stdout == ''
    assert 'error: the following arguments are required' in stderr


TEST_DATA = ['course_with_section', 'course_without_section', 'course_with_framework']


@pytest.mark.parametrize('course_name', TEST_DATA)
def test_course(course_name):
    with tempfile.TemporaryDirectory() as temp_directory:
        prepare_course_directory = PROCESSING_FOLDER / COLLECT_COURSE_STRUCTURE_FOLDER
        command = [sys.executable, (MAIN_FOLDER.parent / 'processing' / 'tasktracker_content_collector.py'),
                   prepare_course_directory / course_name,
                   Path(temp_directory)]
        stdout, stderr = run_in_subprocess(command)
        assert stdout == ''
        assert stderr == ''
        assert len(os.listdir(temp_directory)) == 1
        actual_file = Path(temp_directory) / 'task_content_default.yaml'
        assert actual_file.exists()
        expected_file = (TASKTRACKER_CONTENT_COLLECTOR_FOLDER / f'expected_{course_name}.yaml')
        difference = DeepDiff(parse_yaml(actual_file), parse_yaml(expected_file), ignore_order=True)
        assert not difference
