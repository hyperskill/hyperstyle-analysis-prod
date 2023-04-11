import sys

from core.model.column_name import SubmissionColumns
from core.utils.subprocess_runner import run_in_subprocess
from templates import MAIN_FOLDER
from templates_tests.freq import FREQ_TEMPLATE_ISSUES_FOLDER, SUBMISSIONS_FILE, STEPS_FILE


def test_incorrect_arguments():
    command = [sys.executable, (MAIN_FOLDER.parent / 'freq' / 'search_template_issues.py')]

    stdout, stderr = run_in_subprocess(command)

    assert stdout == ''
    assert 'error: the following arguments are required' in stderr


def test_correct_arguments():
    data_folder = 'template_issues'
    command = [
        sys.executable,
        (MAIN_FOLDER.parent / 'freq' / 'search_template_issues.py'),
        FREQ_TEMPLATE_ISSUES_FOLDER / data_folder / SUBMISSIONS_FILE,
        FREQ_TEMPLATE_ISSUES_FOLDER / data_folder / STEPS_FILE,
        SubmissionColumns.HYPERSTYLE_ISSUES.value,
    ]

    stdout, stderr = run_in_subprocess(command)

    assert stderr == ''
    assert 'name' in stdout
    assert 'description' in stdout
    assert '[2 rows x 9 columns]' in stdout
