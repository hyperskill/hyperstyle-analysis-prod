import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
from pandas._testing import assert_frame_equal

from core.src.utils.df_utils import read_df
from core.src.utils.subprocess_runner import run_in_subprocess
from jba.src import MAIN_FOLDER
from jba.src.models.edu_structure import EduStructureNode, EduStructureType, EduInfoFileField
from jba.src.processing.collect_course_structure import (
    gather_structure,
    _convert_course_structure_to_dataframe,
    convert_course_structure_to_dataframe,
)
from jba.tests.processing import COLLECT_COURSE_STRUCTURE_FOLDER

COURSE_WITH_SECTION_STRUCTURE = EduStructureNode(
    1,
    'course_with_section',
    EduStructureType.COURSE,
    [
        EduStructureNode(
            2,
            'section',
            EduStructureType.SECTION,
            [
                EduStructureNode(
                    3,
                    'lesson',
                    EduStructureType.LESSON,
                    [
                        EduStructureNode(4, 'task1', EduStructureType.TASK, None),
                        EduStructureNode(5, 'task2', EduStructureType.TASK, None),
                        EduStructureNode(6, 'task3', EduStructureType.TASK, None),
                    ],
                )
            ],
        ),
    ],
)


COURSE_WITHOUT_SECTION_STRUCTURE = EduStructureNode(
    1,
    'course_without_section',
    EduStructureType.COURSE,
    [
        EduStructureNode(
            3,
            'lesson',
            EduStructureType.LESSON,
            [
                EduStructureNode(4, 'task1', EduStructureType.TASK, None),
                EduStructureNode(5, 'task2', EduStructureType.TASK, None),
                EduStructureNode(6, 'task3', EduStructureType.TASK, None),
            ],
        )
    ],
)


GATHER_STRUCTURE_TEST_DATA = [
    (
        COLLECT_COURSE_STRUCTURE_FOLDER / 'course_with_section',
        COURSE_WITH_SECTION_STRUCTURE,
    ),
    (
        COLLECT_COURSE_STRUCTURE_FOLDER / 'course_without_section',
        COURSE_WITHOUT_SECTION_STRUCTURE,
    ),
]


@pytest.mark.parametrize(('course_root', 'expected_structure'), GATHER_STRUCTURE_TEST_DATA)
def test_gather_structure(course_root: Path, expected_structure: EduStructureNode):
    actual_structure = gather_structure(course_root)
    assert actual_structure == expected_structure


GATHER_STRUCTURE_THROWS_TEST_DATA = [
    (
        COLLECT_COURSE_STRUCTURE_FOLDER / 'course_with_incorrect_number_of_info_files',
        r'The number of info files in .+ must be exactly 1 \(actual: 2\)\.',
    ),
    (
        COLLECT_COURSE_STRUCTURE_FOLDER / 'course_with_incorrect_number_of_remote_info_files',
        r'The number of remote info files in .+ must be exactly 1 \(actual: 2\)\.',
    ),
    (
        COLLECT_COURSE_STRUCTURE_FOLDER / 'course_with_undefined_structure_type',
        r'Unable to determine a structure type for .+\.',
    ),
    (
        COLLECT_COURSE_STRUCTURE_FOLDER / 'course_with_incorrect_id_field',
        rf'.+ must contain the {EduInfoFileField.ID.value} field\.',
    ),
    (
        COLLECT_COURSE_STRUCTURE_FOLDER / 'course_with_inconsistent_children',
        r'All children nodes inside .+ must have the same structure type\.',
    ),
    (
        COLLECT_COURSE_STRUCTURE_FOLDER / 'course_with_unknown_structure_type',
        "'unknown' is not a valid EduStructureType",
    ),
]


@pytest.mark.parametrize(('course_root', 'expected_message'), GATHER_STRUCTURE_THROWS_TEST_DATA)
def test_gather_structure_throws(course_root: Path, expected_message: str):
    with pytest.raises(ValueError, match=expected_message):
        gather_structure(course_root)


CONVERT_STRUCTURE_TO_DATAFRAME_RECURSIVELY_TEST_DATA = [
    (
        COURSE_WITH_SECTION_STRUCTURE,
        COLLECT_COURSE_STRUCTURE_FOLDER / 'expected_course_with_section_df_structure.csv',
    ),
    (
        COURSE_WITHOUT_SECTION_STRUCTURE,
        COLLECT_COURSE_STRUCTURE_FOLDER / 'expected_course_without_section_df_structure.csv',
    ),
    (
        EduStructureNode(
            1,
            'big_course',
            EduStructureType.COURSE,
            [
                EduStructureNode(
                    2,
                    'section1',
                    EduStructureType.SECTION,
                    [
                        EduStructureNode(
                            4,
                            'lesson1',
                            EduStructureType.LESSON,
                            [
                                EduStructureNode(10, 'task1', EduStructureType.TASK, None),
                                EduStructureNode(11, 'task2', EduStructureType.TASK, None),
                            ],
                        ),
                        EduStructureNode(
                            5,
                            'lesson2',
                            EduStructureType.LESSON,
                            [
                                EduStructureNode(12, 'task1', EduStructureType.TASK, None),
                                EduStructureNode(13, 'task2', EduStructureType.TASK, None),
                            ],
                        ),
                        EduStructureNode(
                            6,
                            'lesson3',
                            EduStructureType.LESSON,
                            [
                                EduStructureNode(14, 'task1', EduStructureType.TASK, None),
                                EduStructureNode(15, 'task2', EduStructureType.TASK, None),
                            ],
                        ),
                    ],
                ),
                EduStructureNode(
                    3,
                    'section2',
                    EduStructureType.SECTION,
                    [
                        EduStructureNode(
                            7,
                            'lesson1',
                            EduStructureType.LESSON,
                            [
                                EduStructureNode(16, 'task1', EduStructureType.TASK, None),
                            ],
                        ),
                        EduStructureNode(
                            8,
                            'lesson2',
                            EduStructureType.LESSON,
                            [
                                EduStructureNode(17, 'task1', EduStructureType.TASK, None),
                                EduStructureNode(18, 'task2', EduStructureType.TASK, None),
                                EduStructureNode(19, 'task3', EduStructureType.TASK, None),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        COLLECT_COURSE_STRUCTURE_FOLDER / 'expected_big_course_df_structure.csv',
    ),
]


@pytest.mark.parametrize(('structure', 'expected_df_path'), CONVERT_STRUCTURE_TO_DATAFRAME_RECURSIVELY_TEST_DATA)
def test_convert_structure_to_dataframe_recursively(structure: EduStructureNode, expected_df_path: Path):
    assert_frame_equal(_convert_course_structure_to_dataframe(structure), read_df(expected_df_path))


CONVERT_COURSE_STRUCTURE_TO_DATAFRAME_TEST_DATA = [
    (
        COLLECT_COURSE_STRUCTURE_FOLDER / 'course_with_section',
        COLLECT_COURSE_STRUCTURE_FOLDER / 'expected_course_with_section.csv',
    ),
    (
        COLLECT_COURSE_STRUCTURE_FOLDER / 'course_without_section',
        COLLECT_COURSE_STRUCTURE_FOLDER / 'expected_course_without_section.csv',
    ),
]


@pytest.mark.parametrize(('course_root', 'expected_structure_path'), CONVERT_COURSE_STRUCTURE_TO_DATAFRAME_TEST_DATA)
def test_convert_course_structure_to_dataframe(course_root: Path, expected_structure_path: Path):
    course_structure = gather_structure(course_root)
    assert_frame_equal(convert_course_structure_to_dataframe(course_structure), read_df(expected_structure_path))


def test_incorrect_arguments():
    stdout, stderr = run_in_subprocess(
        [sys.executable, (MAIN_FOLDER.parent / 'processing' / 'collect_course_structure.py')]
    )

    assert stdout == ''
    assert 'error: the following arguments are required' in stderr


@pytest.mark.parametrize(('course_root', 'expected_structure_path'), CONVERT_COURSE_STRUCTURE_TO_DATAFRAME_TEST_DATA)
def test_correct_arguments(course_root: Path, expected_structure_path: Path):
    with NamedTemporaryFile(suffix='.csv') as output_file:
        stdout, stderr = run_in_subprocess(
            [
                sys.executable,
                (MAIN_FOLDER.parent / 'processing' / 'collect_course_structure.py'),
                str(course_root),
                output_file.name,
            ]
        )

        assert stdout == ''
        assert stderr == ''
        assert_frame_equal(read_df(output_file.name), read_df(expected_structure_path))
