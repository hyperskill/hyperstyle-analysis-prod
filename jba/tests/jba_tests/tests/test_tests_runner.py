import sys

import json

import os
import pandas as pd
import pytest
from bs4 import BeautifulSoup
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory

from core.utils.file.file_utils import create_file
from core.utils.subprocess_runner import run_in_subprocess
from jba import MAIN_FOLDER
from jba.models.edu_columns import EduColumnName, EduTaskStatus, EduCodeSnippetField
from jba.tests.tests_runner import (
    _run_tests,
    GRADLE_STDOUT_LOGS_FILE,
    GRADLE_STDERR_LOGS_FILE,
    TEST_LOGS_FOLDER_NAME,
    _check_submission,
    check_user,
)
from jba_tests.tests import TESTS_FOLDER

TESTS_RUNNER_FOLDER = TESTS_FOLDER / 'tests_runner'

KOTLIN_ONBOARDING_INTRODUCTION_REPO = 'https://github.com/jetbrains-academy/kotlin-onboarding-introduction.git'
KOTLIN_ONBOARDING_INTRODUCTION_COMMIT = '578dbbf8257bd5a3022c4e67bfebbaea4766f246'  # Version before refactoring


@pytest.fixture(scope='session')
def _original_repo(tmp_path_factory) -> Path:
    temp_dir = tmp_path_factory.mktemp('original_repo')
    run_in_subprocess(['git', 'clone', KOTLIN_ONBOARDING_INTRODUCTION_REPO, '.'], working_directory=temp_dir)
    run_in_subprocess(['git', 'checkout', KOTLIN_ONBOARDING_INTRODUCTION_COMMIT], working_directory=temp_dir)
    return temp_dir


@pytest.fixture
def repo(tmp_path_factory, _original_repo: Path) -> Path:
    temp_dir = tmp_path_factory.mktemp('repo')
    copytree(_original_repo, temp_dir, dirs_exist_ok=True)
    return temp_dir


def assert_test_logs(
    logs_path: Path,
    expected_number_of_tests: int,
    expected_number_of_failures: int,
    expected_number_of_ignored: int,
):
    with open(logs_path / TEST_LOGS_FOLDER_NAME / 'index.html') as test_logs:
        test_logs_content = test_logs.read()

    soup = BeautifulSoup(test_logs_content, 'html.parser')

    summary = soup.find('div', {'id': 'summary'})
    number_of_tests = int(summary.find('div', {'id': 'tests'}).find('div', {'class': 'counter'}).text.strip())
    number_of_failures = int(summary.find('div', {'id': 'failures'}).find('div', {'class': 'counter'}).text.strip())
    number_of_ignored = int(summary.find('div', {'id': 'ignored'}).find('div', {'class': 'counter'}).text.strip())

    assert number_of_tests == expected_number_of_tests
    assert number_of_failures == expected_number_of_failures
    assert number_of_ignored == expected_number_of_ignored


def assert_correct_submission(logs_path: Path, expected_number_of_tests: int):
    assert (logs_path / GRADLE_STDOUT_LOGS_FILE).exists()
    assert not (logs_path / GRADLE_STDERR_LOGS_FILE).exists()
    assert (logs_path / TEST_LOGS_FOLDER_NAME).exists()

    with open(logs_path / GRADLE_STDOUT_LOGS_FILE) as stdout_logs:
        assert 'BUILD SUCCESSFUL' in stdout_logs.read()

    assert_test_logs(logs_path, expected_number_of_tests, 0, 0)


def assert_invalid_submission(logs_path: Path, expected_number_of_exception: int):
    assert (logs_path / GRADLE_STDOUT_LOGS_FILE).exists()
    assert (logs_path / GRADLE_STDERR_LOGS_FILE).exists()
    assert not (logs_path / TEST_LOGS_FOLDER_NAME).exists()

    with open(logs_path / GRADLE_STDERR_LOGS_FILE) as stderr_logs:
        stderr_logs_content = stderr_logs.read()

    assert 'BUILD FAILED' in stderr_logs_content

    number_of_exception = sum(1 for line in stderr_logs_content.splitlines() if line.startswith('e: '))
    assert number_of_exception == expected_number_of_exception


def assert_wrong_submission(logs_path: Path, expected_number_of_tests: int, expected_number_of_failures: int):
    assert (logs_path / GRADLE_STDOUT_LOGS_FILE).exists()
    assert (logs_path / GRADLE_STDERR_LOGS_FILE).exists()
    assert (logs_path / TEST_LOGS_FOLDER_NAME).exists()

    with open(logs_path / GRADLE_STDERR_LOGS_FILE) as stderr_logs:
        stderr_logs_content = stderr_logs.read()

    assert 'BUILD FAILED' in stderr_logs_content
    assert 'There were failing tests' in stderr_logs_content

    assert_test_logs(logs_path, expected_number_of_tests, expected_number_of_failures, 0)


def test_run_tests_on_correct_submission(repo: Path):
    task_root_path = repo / 'Introduction' / 'LastPush' / 'FinishTheApp'

    with open(TESTS_RUNNER_FOLDER / 'correct_submission.kt') as correct_submission:
        correct_submission_content = correct_submission.read()
        next(create_file(task_root_path / 'src' / 'main' / 'kotlin' / 'Main.kt', correct_submission_content))

    with TemporaryDirectory() as tmp_dir:
        _run_tests(repo, task_root_path, Path(tmp_dir))
        assert_correct_submission(Path(tmp_dir), expected_number_of_tests=132)


def test_run_tests_on_invalid_submission(repo: Path):
    task_root_path = repo / 'Introduction' / 'LastPush' / 'FinishTheApp'

    with open(TESTS_RUNNER_FOLDER / 'invalid_submission.kt') as invalid_submission:
        invalid_submission_content = invalid_submission.read()
        next(create_file(task_root_path / 'src' / 'main' / 'kotlin' / 'Main.kt', invalid_submission_content))

    with TemporaryDirectory() as tmp_dir:
        _run_tests(repo, task_root_path, Path(tmp_dir))
        assert_invalid_submission(Path(tmp_dir), expected_number_of_exception=8)


def test_run_tests_on_wrong_submission(repo: Path):
    task_root_path = repo / 'Introduction' / 'LastPush' / 'FinishTheApp'

    with open(TESTS_RUNNER_FOLDER / 'wrong_submission.kt') as wrong_submission:
        wrong_submission_content = wrong_submission.read()
        next(create_file(task_root_path / 'src' / 'main' / 'kotlin' / 'Main.kt', wrong_submission_content))

    with TemporaryDirectory() as tmp_dir:
        _run_tests(repo, task_root_path, Path(tmp_dir))
        assert_wrong_submission(Path(tmp_dir), expected_number_of_tests=132, expected_number_of_failures=110)


SUBMISSION_BASE_DATA = {
    EduColumnName.ID.value: 42,
    EduColumnName.STATUS.value: EduTaskStatus.CORRECT.value,
    EduColumnName.SECTION_NAME.value: 'Introduction',
    EduColumnName.LESSON_NAME.value: 'LastPush',
    EduColumnName.TASK_NAME.value: 'FinishTheApp',
}


def test_check_submission_empty_snippets(repo: Path):
    with TemporaryDirectory() as tmp_dir:
        _check_submission(
            pd.Series({EduColumnName.CODE_SNIPPETS.value: None, **SUBMISSION_BASE_DATA}),
            repo,
            Path(tmp_dir),
        )

        assert len(os.listdir(tmp_dir)) == 0


def test_check_submission(repo: Path):
    with open(TESTS_RUNNER_FOLDER / 'code_snippets.json') as file:
        code_snippets = file.read()

    task_root_path = (
        repo
        / SUBMISSION_BASE_DATA[EduColumnName.SECTION_NAME.value]
        / SUBMISSION_BASE_DATA[EduColumnName.LESSON_NAME.value]
        / SUBMISSION_BASE_DATA[EduColumnName.TASK_NAME.value]
    )

    modification_time_before = {}
    for snippet in json.loads(code_snippets):
        file_path = snippet[EduCodeSnippetField.NAME.value]
        try:
            modification_time_before[file_path] = os.path.getmtime(task_root_path / file_path)
        except FileNotFoundError:
            continue

    with TemporaryDirectory() as tmp_dir:
        _check_submission(
            pd.Series({EduColumnName.CODE_SNIPPETS.value: code_snippets, **SUBMISSION_BASE_DATA}),
            repo,
            Path(tmp_dir),
        )

        assert (Path(tmp_dir) / '42').exists()
        assert_wrong_submission(Path(tmp_dir) / '42', expected_number_of_tests=132, expected_number_of_failures=110)

    assert not (task_root_path / 'src/main/kotlin/where_did_you_come_from.txt').exists()

    modification_time_after = {}
    for snippet in json.loads(code_snippets):
        file_path = snippet[EduCodeSnippetField.NAME.value]
        try:
            modification_time_after[file_path] = os.path.getmtime(task_root_path / file_path)
        except FileNotFoundError:
            continue

    main_kt_path = 'src/main/kotlin/Main.kt'
    assert modification_time_before.pop(main_kt_path) != modification_time_after.pop(main_kt_path)

    # Checking that other files wasn't modified
    assert set(modification_time_before.items()) == set(modification_time_after.items())


def test_check_user_submissions_repo_copying(repo: Path):
    submissions = pd.read_csv(TESTS_RUNNER_FOLDER / 'submissions.csv')
    user_submissions = submissions[submissions[EduColumnName.USER_ID.value] == 1]

    modification_time_before = {}
    for root, dirs, files in os.walk(repo):
        for file in files:
            file_path = Path(root) / file
            modification_time_before[file_path] = os.path.getmtime(file_path)

    with TemporaryDirectory() as tmp_dir:
        check_user(user_submissions, repo, Path(tmp_dir))

    modification_time_after = {}
    for root, dirs, files in os.walk(repo):
        for file in files:
            file_path = Path(root) / file
            modification_time_after[file_path] = os.path.getmtime(file_path)

    # Checking that files inside repo wasn't modified
    assert set(modification_time_before.items()) == set(modification_time_after.items())


SUBMISSION_ASSERT_FUNCTION_AND_ARGS = {
    0: (assert_invalid_submission, 8),
    1: (assert_wrong_submission, 132, 110),
    2: (assert_invalid_submission, 3),
    3: (assert_correct_submission, 87),
    4: (assert_invalid_submission, 3),
    5: (assert_correct_submission, 87),
    6: (assert_correct_submission, 132),
}


def test_check_user_submissions(repo: Path):
    submissions = pd.read_csv(TESTS_RUNNER_FOLDER / 'submissions.csv')
    user_submissions = submissions[submissions[EduColumnName.USER_ID.value] == 1]

    with TemporaryDirectory() as tmp_dir:
        check_user(user_submissions, repo, Path(tmp_dir))

        modification_times = []
        for i in [*range(4), 6]:
            submissions_logs_folder = Path(tmp_dir) / str(i)

            assert submissions_logs_folder.exists()
            assert_submission, *args = SUBMISSION_ASSERT_FUNCTION_AND_ARGS[i]
            assert_submission(submissions_logs_folder, *args)

            modification_times.append(os.path.getmtime(submissions_logs_folder))

    # Checking that modification times is in ascending order
    assert sorted(modification_times) == modification_times


def test_functional_incorrect_arguments(repo: Path):
    command = [sys.executable, (MAIN_FOLDER.parent / 'tests' / 'tests_runner.py')]

    stdout, stderr = run_in_subprocess(command)

    assert stdout == ''
    assert 'error: the following arguments are required' in stderr


def test_functional(repo: Path):
    with TemporaryDirectory() as tmp_dir:
        command = [
            sys.executable,
            (MAIN_FOLDER.parent / 'tests' / 'tests_runner.py'),
            (TESTS_RUNNER_FOLDER / 'submissions.csv'),
            repo,
            tmp_dir,
        ]

        run_in_subprocess(command)

        for submission_id, (assert_submission, *args) in SUBMISSION_ASSERT_FUNCTION_AND_ARGS.items():
            submissions_logs_folder = Path(tmp_dir) / str(submission_id)
            assert submissions_logs_folder.exists()
            assert_submission(submissions_logs_folder, *args)
