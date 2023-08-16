import sys

from core.src.utils.subprocess_runner import run_in_subprocess
from data_labelling.src import MAIN_FOLDER


def test_incorrect_arguments():
    command = [sys.executable, (MAIN_FOLDER.parent / 'hyperstyle' / 'evaluate.py')]

    stdout, stderr = run_in_subprocess(command)

    assert stdout == ''
    assert 'error: the following arguments are required' in stderr
