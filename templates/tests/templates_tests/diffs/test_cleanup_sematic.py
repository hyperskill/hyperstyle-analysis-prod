from typing import List

import pytest

from src.templates.diffs.filter_by_diff import to_cleanup_semantic

CLEANUP_SEMANTIC_TEST_DATA = [
    (
        [
            "def foo():\n\n",
            "    # You already are within the body of func foo()\n",
            "    # Declare and assign the correct value to the 'varchest' variable below:\n\n",
            "    print(varchest)"
        ],
        [
            "def foo():\n\n",
            "    varchest = \"gold\"\n\n",
            "    print(varchest)"
        ],
        True,
    ),
    (
        [
            "def foo():\n\n",
            "    print(varchest)"
        ],
        [
            "def foo():\n\n",
            "    # Some comment"
            "    varchest = \"gold\"\n\n",
            "    print(varchest)"
        ],
        True,
    ),
    (
        [
            "def foo():\n\n",
            "    # Comment 1"
            "    print(varchest)"
        ],
        [
            "def foo():\n\n",
            "    # Comment 2"
            "    varchest = \"gold\"\n\n",
            "    print(varchest)"
        ],
        True,
    ),
    (
        [
            "def foo():\n\n",
            "    # Comment 1"
            "    print(varchest)"
        ],
        [
            "def foo():\n\n",
            "    # Comment 2"
            "    varchest = \"gold\"\n\n",
            "    print(varchest)"
        ],
        True,
    ),
    (
        [
            "def foo():\n\n",
            "    # You already are within the body of func foo()\n",
            "    # Declare and assign the correct value to the 'varchest' variable below:\n\n",
            "    print(varchest)"
        ],
        [
            "def foo():\n\n",
            "    # You already are within the body of func foo()\n",
            "    # Declare and assign the correct value to the 'varchest' variable below:\n\n",
            "    varchest = \"gold\"\n\n",
            "    print(varchest)"
        ],
        False,
    ),
    (
        [
            "def foo():\n\n",
            "    # You already are within the body of func foo()\n",
            "    # Declare and assign the correct value to the 'varchest' variable below:\n\n",
            "    print(varchest)"
        ],
        [
            "def foo():\n\n",
            "    varchest = \"gold\"\n\n",
            "    print(varchest)"
            "    # You already are within the body of func foo()\n",
            "    # Declare and assign the correct value to the 'varchest' variable below:\n\n",
        ],
        False,
    ),
]


@pytest.mark.parametrize(('template', 'code', 'expected'), CLEANUP_SEMANTIC_TEST_DATA)
def test_to_cleanup_semantic(template: List[str],
                             code: List[str],
                             expected: bool):
    assert to_cleanup_semantic(template, code) == expected
