import sys

from core.src.utils.subprocess_runner import run_in_subprocess
from jba.src import MAIN_FOLDER


def test_incorrect_arguments():
    command = [sys.executable, (MAIN_FOLDER.parent / 'processing' / 'data_processing.py')]

    stdout, stderr = run_in_subprocess(command)

    assert stdout == ''
    assert 'error: the following arguments are required' in stderr
