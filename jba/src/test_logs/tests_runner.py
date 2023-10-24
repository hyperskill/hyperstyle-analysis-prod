import argparse
import json
import logging
import subprocess
import time
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory
from typing import Optional

import pandas as pd
from pandarallel import pandarallel
from pandarallel.core import NB_PHYSICAL_CORES

from core.src.utils.df_utils import read_df
from core.src.utils.file.extension_utils import AnalysisExtension
from core.src.utils.file.file_utils import create_file
from core.src.utils.file.yaml_utils import read_yaml_field_content
from core.src.utils.parsing_utils import str_to_datetime
from core.src.utils.subprocess_runner import run_in_subprocess
from jba.src.models.edu_columns import EduColumnName, EduConfigField, EduCodeSnippetField

logger = logging.getLogger(__name__)

GRADLE_STDOUT_LOGS_FILE = 'gradle_stdout.log'
GRADLE_STDERR_LOGS_FILE = 'gradle_stderr.log'
TEST_LOGS_FOLDER_NAME = 'test_logs'


def _run_tests(course_root_path: Path, task_root_path: Path, output_path: Path, timeout: Optional[float] = None):
    """
    Run task tests and save logs.

    :param course_root_path: Path to the course root.
    :param task_root_path: Path to the task root.
    :param output_path: Path to the folder to store logs.
    :param timeout: Timeout in seconds for subprocess to be executed.
    """
    module_name = "-".join(task_root_path.relative_to(course_root_path).parts)
    submission_id = output_path.name

    start = time.time()

    gradle_clean_task = f':{module_name}:clean'
    logger.info(f'Running {gradle_clean_task} for submission#{submission_id}')
    try:
        run_in_subprocess(['./gradlew', gradle_clean_task], working_directory=course_root_path, timeout=timeout)
    except subprocess.TimeoutExpired:
        logger.error(f'Timeout expired while running {gradle_clean_task} for submission#{submission_id}')
        return

    gradle_test_task = f':{module_name}:test'
    logger.info(f'Running {gradle_test_task} for submission#{submission_id}')
    try:
        stdout, stderr = run_in_subprocess(
            ['./gradlew', gradle_test_task],
            working_directory=course_root_path,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        logger.error(f'Timeout expired while running {gradle_test_task} for submission#{submission_id}')
        return

    finish = time.time()

    logger.info(f'Submission#{submission_id} run in {finish - start}s')

    output_path.mkdir(parents=True, exist_ok=True)

    if stdout:
        next(create_file(output_path / GRADLE_STDOUT_LOGS_FILE, stdout))

    if stderr:
        next(create_file(output_path / GRADLE_STDERR_LOGS_FILE, stderr))

    test_logs = task_root_path / 'build' / 'reports' / 'tests' / 'test'
    if test_logs.exists():
        copytree(test_logs, output_path / TEST_LOGS_FOLDER_NAME, dirs_exist_ok=True)


def _check_submission(
    submission: pd.Series,
    course_root_path: Path,
    output_path: Path,
    timeout: Optional[float] = None,
):
    """
    Run tests on user's submission and save logs.

    :param submission: User's submission data.
    :param course_root_path: Path to the course root.
    :param output_path: Path to the folder to store logs.
    :param timeout: Timeout in seconds for subprocess to be executed.
    """
    submission_id = submission.at[EduColumnName.ID.value]
    logger.info(f'Checking submission#{submission_id}')

    if pd.isna(submission[EduColumnName.CODE_SNIPPETS.value]):
        logger.warning(f'Code snippets are missing for submission#{submission_id}')
        return

    section_name = submission.get(EduColumnName.SECTION_NAME.value)
    lesson_name = submission[EduColumnName.LESSON_NAME.value]
    task_name = submission[EduColumnName.TASK_NAME.value]

    # The nested ternary operator is justified here
    task_root_path = (
        course_root_path / ('' if section_name is None else section_name) / lesson_name / task_name  # noqa: WPS509
    )

    files_info = read_yaml_field_content(
        task_root_path / f'task-info{AnalysisExtension.YAML.value}', EduConfigField.FILES.value
    )

    visible_files = {
        file_info[EduConfigField.NAME.value] for file_info in files_info if file_info[EduConfigField.VISIBLE.value]
    }
    logger.debug(f'Visible files for submission#{submission_id}: {visible_files}')

    snippets = {
        task_root_path / snippet[EduCodeSnippetField.NAME.value]: snippet[EduCodeSnippetField.TEXT.value]
        for snippet in json.loads(submission[EduColumnName.CODE_SNIPPETS.value])
        if snippet[EduCodeSnippetField.NAME.value] in visible_files
    }
    logger.debug(f'Snippets for submissions#{submission_id}: {snippets.keys()}')

    for snippet_path, snippet_content in snippets.items():
        logger.debug(f'Replacing {snippet_path} with the snippet content for submissions#{submission_id}')
        next(create_file(snippet_path, snippet_content))

    _run_tests(course_root_path, task_root_path, output_path / str(submission_id), timeout=timeout)


def check_user(
    user_submissions: pd.DataFrame,
    course_root_path: Path,
    output_path: Path,
    timeout: Optional[float] = None,
):
    """
    Run tests on user's submissions and save logs.

    :param user_submissions: User's submissions.
    :param course_root_path: Path to the course root.
    :param output_path: Path to the folder to store logs.
    :param timeout: Timeout in seconds for subprocess to be executed.
    """
    user_id = user_submissions.iat[0, user_submissions.columns.get_loc(EduColumnName.USER_ID.value)]

    logger.info(f'Checking user#{user_id}')

    with TemporaryDirectory() as tmpdir:
        logger.info(f'Coping the course for user#{user_id}')
        copytree(course_root_path, tmpdir, dirs_exist_ok=True)

        user_submissions[EduColumnName.SUBMISSION_DATETIME.value] = user_submissions[
            EduColumnName.SUBMISSION_DATETIME.value
        ].map(str_to_datetime)

        user_submissions.sort_values(EduColumnName.SUBMISSION_DATETIME.value).apply(
            lambda submission_data: _check_submission(submission_data, Path(tmpdir), output_path, timeout=timeout),
            axis=1,
        )


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        'submissions_path',
        type=lambda value: Path(value).absolute(),
        help='Path to .csv file with submissions.',
    )

    parser.add_argument(
        'course_sources_path',
        type=lambda value: Path(value).absolute(),
        help='Path to course sources.',
    )

    parser.add_argument(
        'logs_output_path',
        type=lambda value: Path(value).absolute(),
        help='Path to the folder to store logs.',
    )

    parser.add_argument('--timeout', type=float, help='Timeout in seconds for subprocess to be executed.')

    parser.add_argument(
        '--n-cpu',
        type=int,
        help='Number of CPUs to use for parallel execution.',
        default=NB_PHYSICAL_CORES,
    )

    parser.add_argument(
        '--debug',
        help='Run the script in debug mode.',
        action='store_true',
    )

    parser.add_argument(
        '--script-logs-path',
        type=lambda value: Path(value).absolute(),
        help='Path to a file where to save script logs.',
    )


def main():
    parser = argparse.ArgumentParser()
    configure_parser(parser)
    args = parser.parse_args()

    logging.basicConfig(
        filename=args.script_logs_path,
        level=logging.DEBUG if args.debug else logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',  # noqa: WPS323 You must use % here to format logger.
    )
    pandarallel.initialize(nb_workers=args.n_cpu)

    if args.timeout is None:
        logger.warning(
            f"The timeout arguments is not specified. "
            f"If some solution has an infinite loop, the script will never complete!"
        )

    submissions = read_df(args.submissions_path)

    submissions.groupby(EduColumnName.USER_ID.value, as_index=False).parallel_apply(
        check_user,
        args.course_sources_path,
        args.logs_output_path,
        args.timeout,
    )


if __name__ == '__main__':
    main()
