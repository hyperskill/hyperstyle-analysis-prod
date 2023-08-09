from typing import List

import pytest

from templates.src.diffs.filter_by_diff import get_template_to_code_diffs
from templates.src.diffs.model.diff_result import DiffResult
from templates.tests.diffs.code_template_diff_data.code_template_diff_data_java import DIFF_TEST_DATA_JAVA
from templates.tests.diffs.code_template_diff_data.code_template_diff_data_kotlin import DIFF_TEST_DATA_KOTLIN
from templates.tests.diffs.code_template_diff_data.code_template_diff_data_python import DIFF_TEST_DATA_PYTHON


@pytest.mark.parametrize(('template', 'code', 'expected_diffs'), DIFF_TEST_DATA_PYTHON)
def test_filter_template_issues_using_diff_for_python(template: List[str],
                                                      code: List[str],
                                                      expected_diffs: List[DiffResult]):
    diffs = get_template_to_code_diffs(template, code)
    assert diffs == expected_diffs


@pytest.mark.parametrize(('template', 'code', 'expected_diffs'), DIFF_TEST_DATA_JAVA)
def test_filter_template_issues_using_diff_for_java(template: List[str],
                                                    code: List[str],
                                                    expected_diffs: List[DiffResult]):
    diffs = get_template_to_code_diffs(template, code)
    assert diffs == expected_diffs


@pytest.mark.parametrize(('template', 'code', 'expected_diffs'), DIFF_TEST_DATA_KOTLIN)
def test_filter_template_issues_using_diff_for_java(template: List[str],
                                                    code: List[str],
                                                    expected_diffs: List[DiffResult]):
    diffs = get_template_to_code_diffs(template, code)
    assert diffs == expected_diffs
