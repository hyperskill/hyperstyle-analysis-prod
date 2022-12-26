from core.model.column_name import SubmissionColumns
from core.utils.df_utils import read_df, equal_df
from core.utils.subprocess_runner import run_in_subprocess
from preprocessing import MAIN_FOLDER
from preprocessing_tests import PREPROCESSING_FOLDER, SUBMISSIONS_FILE

DIFF_TEST_DATA = [
    (
        ['python3', (MAIN_FOLDER.parent / 'diffs' / 'filter_by_dif.py')],
     ),
]


def test_incorrect_arguments():
    command = ['python3', (MAIN_FOLDER.parent / 'preprocess_submissions.py')]

    stdout, stderr = run_in_subprocess(command)

    assert stdout == ''
    assert 'error: the following arguments are required' in stderr


def test_correct_arguments():
    command = [
        'python3',
        (MAIN_FOLDER.parent / 'preprocess_submissions.py'),
        PREPROCESSING_FOLDER / SUBMISSIONS_FILE,
    ]

    stdout, stderr = run_in_subprocess(command)
    assert stderr == ''
    assert SubmissionColumns.GROUP.value in stdout
    assert SubmissionColumns.ATTEMPT.value in stdout
    assert SubmissionColumns.TOTAL_ATTEMPTS.value in stdout
    assert '[6 rows x 8 columns]' in stdout


def test_output_with_correct_arguments():
    output_file = PREPROCESSING_FOLDER / 'preprocessed_submissions.csv'
    command = [
        'python3',
        (MAIN_FOLDER.parent / 'preprocess_submissions.py'),
        PREPROCESSING_FOLDER / SUBMISSIONS_FILE,
        output_file
    ]

    stdout, stderr = run_in_subprocess(command)
    assert stderr == ''
    assert stdout == ''

    actual_df = read_df(output_file)
    expected_df = read_df(PREPROCESSING_FOLDER / 'preprocessed_submissions_expected.csv')
    equal_df(expected_df, actual_df)
