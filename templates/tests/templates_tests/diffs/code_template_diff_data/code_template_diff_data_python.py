from templates.diffs.model.diff_interval import DiffInterval
from templates.diffs.model.diff_result import DiffResult
from templates.diffs.model.diff_tag import DiffTag

DIFF_TEST_DATA_PYTHON = [
    (
        ["a = 1\n", "b = 2\n", "c = # put your code here\n", "print(a, b, c)"],
        ["a = 1\n", "b = 2\n", "c = 3\n", "print(a, b, c)"],
        [
            DiffResult(DiffTag.EQUAL.value, "a = 1\nb = 2\nc = ", DiffInterval(0, 16), DiffInterval(0, 16)),
            DiffResult(DiffTag.DELETION.value, "# put your code here", DiffInterval(16, 36), DiffInterval(16, 16)),
            DiffResult(DiffTag.ADDITION.value, "3", DiffInterval(36, 36), DiffInterval(16, 17)),
            DiffResult(DiffTag.EQUAL.value, "\nprint(a, b, c)", DiffInterval(36, 51), DiffInterval(17, 32))]
    ),
    (
        ["a = 1\n", "b = 2\n", "c = # put your code here\n", "print(a, b, c)"],
        ["A = 1\n", "b = 2\n", "c = 3\n", "print(a, b, c)"],
        [
            DiffResult(DiffTag.DELETION.value, "a", DiffInterval(0, 1), DiffInterval(0, 0)),
            DiffResult(DiffTag.ADDITION.value, "A", DiffInterval(1, 1), DiffInterval(0, 1)),
            DiffResult(DiffTag.EQUAL.value, " = 1\nb = 2\nc = ", DiffInterval(1, 16), DiffInterval(1, 16)),
            DiffResult(DiffTag.DELETION.value, "# put your code here", DiffInterval(16, 36), DiffInterval(16, 16)),
            DiffResult(DiffTag.ADDITION.value, "3", DiffInterval(36, 36), DiffInterval(16, 17)),
            DiffResult(DiffTag.EQUAL.value, "\nprint(a, b, c)", DiffInterval(36, 51), DiffInterval(17, 32))]
    ),
    (
        ["# a = 1"],
        ["a = 1"],
        [
            DiffResult(DiffTag.DELETION.value, "# ", DiffInterval(0, 2), DiffInterval(0, 0)),
            DiffResult(DiffTag.EQUAL.value, "a = 1", DiffInterval(2, 7), DiffInterval(0, 5))]),
    # Lines swap does not work properly
    (
        ["a = 1\n", "b = 2\n", "c = 3\n"],
        ["b = 2\n", "a = 1\n", "c = 3\n"],
        [
            DiffResult(DiffTag.DELETION.value, "a", DiffInterval(0, 1), DiffInterval(0, 0)),
            DiffResult(DiffTag.ADDITION.value, "b", DiffInterval(1, 1), DiffInterval(0, 1)),
            DiffResult(DiffTag.EQUAL.value, " = ", DiffInterval(1, 4), DiffInterval(1, 4)),

            DiffResult(DiffTag.DELETION.value, "1", DiffInterval(4, 5), DiffInterval(4, 4)),
            DiffResult(DiffTag.ADDITION.value, "2", DiffInterval(5, 5), DiffInterval(4, 5)),
            DiffResult(DiffTag.EQUAL.value, "\n", DiffInterval(5, 6), DiffInterval(5, 6)),

            DiffResult(DiffTag.DELETION.value, "b", DiffInterval(6, 7), DiffInterval(6, 6)),
            DiffResult(DiffTag.ADDITION.value, "a", DiffInterval(7, 7), DiffInterval(6, 7)),
            DiffResult(DiffTag.EQUAL.value, " = ", DiffInterval(7, 10), DiffInterval(7, 10)),

            DiffResult(DiffTag.DELETION.value, "2", DiffInterval(10, 11), DiffInterval(10, 10)),
            DiffResult(DiffTag.ADDITION.value, "1", DiffInterval(11, 11), DiffInterval(10, 11)),
            DiffResult(DiffTag.EQUAL.value, "\nc = 3\n", DiffInterval(11, 18), DiffInterval(11, 18))]
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
        ],
        [
            DiffResult(DiffTag.EQUAL.value, "def foo():\n\n    ", DiffInterval(0, 16), DiffInterval(0, 16)),
            DiffResult(DiffTag.DELETION.value,
                       "# You already are within the body of func foo()\n    # Declare and assign the correct value to the 'varchest' variable below:",
                       DiffInterval(16, 140), DiffInterval(16, 16)),
            DiffResult(DiffTag.ADDITION.value, "varchest = \"gold\"", DiffInterval(140, 140), DiffInterval(16, 33)),
            DiffResult(DiffTag.EQUAL.value, "\n\n    print(varchest)", DiffInterval(140, 161), DiffInterval(33, 54)),
        ]
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
            "    # Declare and assign the correct value to the 'valchest' variable below:\n\n",
            "    print(varchest)"
        ],
        [
            DiffResult(DiffTag.EQUAL.value,
                       "def foo():\n\n    # You already are within the body of func foo()\n    # Declare and assign the correct value to the 'va",
                       DiffInterval(0, 117), DiffInterval(0, 117)),
            DiffResult(DiffTag.DELETION.value, "r", DiffInterval(117, 118), DiffInterval(117, 117)),
            DiffResult(DiffTag.ADDITION.value, "l", DiffInterval(118, 118), DiffInterval(117, 118)),
            DiffResult(DiffTag.EQUAL.value, "chest' variable below:\n\n    print(varchest)", DiffInterval(118, 161),
                       DiffInterval(118, 161)),
        ]
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
            "    # Declare and assign the correct value to the 'valchest' variable below:\n\n",
            "    varchest = \"gold\"\n\n",
            "    print(varchest)"
        ],
        [
            DiffResult(DiffTag.EQUAL.value,
                       "def foo():\n\n    # You already are within the body of func foo()\n    # Declare and assign the correct value to the 'va",
                       DiffInterval(0, 117), DiffInterval(0, 117)),
            DiffResult(DiffTag.DELETION.value, "r", DiffInterval(117, 118), DiffInterval(117, 117)),
            DiffResult(DiffTag.ADDITION.value, "l", DiffInterval(118, 118), DiffInterval(117, 118)),
            DiffResult(DiffTag.EQUAL.value, "chest' variable below:\n\n", DiffInterval(118, 142),
                       DiffInterval(118, 142)),
            DiffResult(DiffTag.ADDITION.value, "    varchest = \"gold\"\n\n", DiffInterval(142, 142),
                       DiffInterval(142, 165)),
            DiffResult(DiffTag.EQUAL.value, "    print(varchest)", DiffInterval(142, 161), DiffInterval(165, 184)),
        ]
    ),

    (
        ["a = 1\n", "b = 2\n", "c = # add value 'cat'\n", "print(a, b, c)"],
        ["a = 1\n", "b = 2\n", "c = 'cat'\n", "print(a, b, c)"],
        [
            DiffResult(DiffTag.EQUAL.value, "a = 1\nb = 2\nc = ", DiffInterval(0, 16), DiffInterval(0, 16)),
            DiffResult(DiffTag.DELETION.value, "# add value ", DiffInterval(16, 28), DiffInterval(16, 16)),
            DiffResult(DiffTag.EQUAL.value, "'cat'\nprint(a, b, c)", DiffInterval(28, 48), DiffInterval(16, 36))]
    ),
]
