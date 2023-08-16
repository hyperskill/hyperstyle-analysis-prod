import sys

from core.src.model.column_name import SubmissionColumns
from core.src.utils.subprocess_runner import run_in_subprocess
from templates.src import MAIN_FOLDER
from templates.tests.freq import FREQ_TEMPLATE_ISSUES_FOLDER, SUBMISSIONS_FILE, TEMPLATES_ISSUES_FILE


def test_incorrect_arguments():
    command = [sys.executable, (MAIN_FOLDER.parent / 'freq' / 'postprocess.py')]

    stdout, stderr = run_in_subprocess(command)

    assert stdout == ''
    assert 'error: the following arguments are required' in stderr


def test_correct_arguments():
    data_folder = 'template_issues'
    command = [
        sys.executable,
        (MAIN_FOLDER.parent / 'freq' / 'postprocess.py'),
        FREQ_TEMPLATE_ISSUES_FOLDER / data_folder / TEMPLATES_ISSUES_FILE,
        FREQ_TEMPLATE_ISSUES_FOLDER / data_folder / SUBMISSIONS_FILE,
        SubmissionColumns.HYPERSTYLE_ISSUES.value,
    ]

    stdout, stderr = run_in_subprocess(command)

    assert stderr == ''
    assert 'Empty DataFrame' in stdout
    assert 'Columns: [name, description, line, pos_in_template, count, groups, total_count, step_id, frequency]' \
           in stdout
    assert 'Columns: [name, description, line, pos_in_template, count, groups, total_count, step_id, frequency]' \
           in stdout
    assert '[1 rows x 9 columns]' in stdout
