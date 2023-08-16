import sys

from core.src.utils.subprocess_runner import run_in_subprocess
from data_collection.src import MAIN_FOLDER


def test_incorrect_arguments():
    command = [sys.executable, (MAIN_FOLDER.parent / 'collect_data.py')]

    stdout, stderr = run_in_subprocess(command)

    assert stdout == ''
    assert 'error: the following arguments are required' in stderr


def test_correct_arguments():
    command = [
        sys.executable,
        (MAIN_FOLDER.parent / 'collect_data.py'),
        'hyperskill',
        'step',
        './data_collection/src/resources',
    ]

    stdout, stderr = run_in_subprocess(command)

    assert 'You need to specify CLIENT_ID for the platform' in stderr
