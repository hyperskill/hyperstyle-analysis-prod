import sys

from core.src.model.column_name import SubmissionColumns
from core.src.utils.subprocess_runner import run_in_subprocess
from templates.src import MAIN_FOLDER
from templates.tests.diffs import SUBMISSIONS_FILE, DIFF_TEMPLATE_ISSUES_FOLDER, STEPS_FILE


def test_incorrect_arguments():
    command = [sys.executable, (MAIN_FOLDER.parent / 'diffs' / 'filter_by_diff.py')]

    stdout, stderr = run_in_subprocess(command)

    assert stdout == ''
    assert 'error: the following arguments are required' in stderr


def test_correct_arguments():
    command = [
        sys.executable,
        (MAIN_FOLDER.parent / 'diffs' / 'filter_by_diff.py'),
        DIFF_TEMPLATE_ISSUES_FOLDER / SUBMISSIONS_FILE,
        DIFF_TEMPLATE_ISSUES_FOLDER / STEPS_FILE,
        SubmissionColumns.HYPERSTYLE_ISSUES.value,
    ]

    stdout, stderr = run_in_subprocess(command)

    assert stderr == ''
    assert 'hyperstyle_issues_diff_template_positions' in stdout
    assert '[7 rows x 13 columns]' in stdout
