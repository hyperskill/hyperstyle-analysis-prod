import pytest

from core.utils.df_utils import read_df, equal_df
from jba.processing.prepare_course_data import _gather_course_structure
from jba_tests.processing import PROCESSING_FOLDER

COURSE_TEST_DATA = [
    (
        (PROCESSING_FOLDER / 'course_example'),
        (PROCESSING_FOLDER / 'course_1_structure_expected.csv')
    )
]


@pytest.mark.parametrize(('course_root', 'expected_table'), COURSE_TEST_DATA)
def test_to_cleanup_semantic(course_root: str, expected_table: str):
    tasks_info_df = _gather_course_structure(course_root)
    expected_df = read_df(expected_table)
    equal_df(expected_df, tasks_info_df)
