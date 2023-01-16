from src.templates.diffs.model.diff_interval import DiffInterval
from src.templates.diffs.model.diff_result import DiffResult
from src.templates.diffs.model.diff_tag import DiffTag

DIFF_TEST_DATA_KOTLIN = [
    (
        [
            "fun main() {\n",
            "    val a = 1\n",
            "    val b = 2\n",
            "    val c = // put your code here\n",
            "    println(\"$a $b $c\")\n"
            "}"
        ],
        [
            "fun main() {\n",
            "    val a = 1\n",
            "    val b = 2\n",
            "    val c = 3\n",
            "    println(\"$a $b $c\")\n"
            "}"
        ],
        [
            DiffResult(DiffTag.EQUAL.value,
                       "fun main() {\n    val a = 1\n    val b = 2\n    val c = ",
                       DiffInterval(0, 53), DiffInterval(0, 53)),
            DiffResult(DiffTag.DELETION.value, "// put your code here", DiffInterval(53, 74), DiffInterval(53, 53)),
            DiffResult(DiffTag.ADDITION.value, "3", DiffInterval(74, 74), DiffInterval(53, 54)),
            DiffResult(DiffTag.EQUAL.value, "\n    println(\"$a $b $c\")\n}", DiffInterval(74, 100),
                       DiffInterval(54, 80))
        ]
    ),

    (
        [
            "fun main() {\n",
            "    val a = 1\n",
            "    val b = 2\n",
            "    val c = // put your code here\n",
            "    println(\"$a $b $c\")\n"
            "}"
        ],
        [
            "fun main() {\n",
            "    val A = 1\n",
            "    val b = 2\n",
            "    val c = 3\n",
            "    println(\"$a $b $c\")\n"
            "}"
        ],
        [
            DiffResult(DiffTag.EQUAL.value,
                       "fun main() {\n    val ",
                       DiffInterval(0, 21), DiffInterval(0, 21)),
            DiffResult(DiffTag.DELETION.value, "a", DiffInterval(21, 22), DiffInterval(21, 21)),
            DiffResult(DiffTag.ADDITION.value, "A", DiffInterval(22, 22), DiffInterval(21, 22)),
            DiffResult(DiffTag.EQUAL.value,
                       " = 1\n    val b = 2\n    val c = ",
                       DiffInterval(22, 53), DiffInterval(22, 53)),
            DiffResult(DiffTag.DELETION.value, "// put your code here", DiffInterval(53, 74), DiffInterval(53, 53)),
            DiffResult(DiffTag.ADDITION.value, "3", DiffInterval(74, 74), DiffInterval(53, 54)),
            DiffResult(DiffTag.EQUAL.value, "\n    println(\"$a $b $c\")\n}", DiffInterval(74, 100),
                       DiffInterval(54, 80))
        ],
    ),

    (
        [
            "fun main() {\n",
            "    val a = 1\n",
            "    val b = 2\n",
            "    val c = 3\n",
            "    println(\"$a $b $c\")\n"
            "}"
        ],
        [
            "fun main() {\n",
            "    val b = 2\n",
            "    val a = 1\n",
            "    val c = 3\n",
            "    println(\"$a $b $c\")\n"
            "}"
        ],
        # Lines swap does not work properly
        [
            DiffResult(DiffTag.EQUAL.value,
                       "fun main() {\n    val ",
                       DiffInterval(0, 21), DiffInterval(0, 21)),
            DiffResult(DiffTag.DELETION.value, "a", DiffInterval(21, 22), DiffInterval(21, 21)),
            DiffResult(DiffTag.ADDITION.value, "b", DiffInterval(22, 22), DiffInterval(21, 22)),
            DiffResult(DiffTag.EQUAL.value, " = ", DiffInterval(22, 25), DiffInterval(22, 25)),

            DiffResult(DiffTag.DELETION.value, "1", DiffInterval(25, 26), DiffInterval(25, 25)),
            DiffResult(DiffTag.ADDITION.value, "2", DiffInterval(26, 26), DiffInterval(25, 26)),
            DiffResult(DiffTag.EQUAL.value, "\n    val ", DiffInterval(26, 35), DiffInterval(26, 35)),

            DiffResult(DiffTag.DELETION.value, "b", DiffInterval(35, 36), DiffInterval(35, 35)),
            DiffResult(DiffTag.ADDITION.value, "a", DiffInterval(36, 36), DiffInterval(35, 36)),
            DiffResult(DiffTag.EQUAL.value, " = ", DiffInterval(36, 39), DiffInterval(36, 39)),

            DiffResult(DiffTag.DELETION.value, "2", DiffInterval(39, 40), DiffInterval(39, 39)),
            DiffResult(DiffTag.ADDITION.value, "1", DiffInterval(40, 40), DiffInterval(39, 40)),
            DiffResult(DiffTag.EQUAL.value, "\n    val c = 3\n    println(\"$a $b $c\")\n}", DiffInterval(40, 80),
                       DiffInterval(40, 80)),
        ]
    ),
    (
        [
            "fun main() {\n\n",
            "    // You already are within the body of func main()\n",
            "    // Declare and assign the correct value to the 'chest' variable below:\n\n",
            "    println(chest)\n"
            "}",
        ],
        [
            "fun main() {\n\n",
            "    var chest = \"gold\"\n\n",
            "    println(chest)\n"
            "}",
        ],
        [
            DiffResult(DiffTag.EQUAL.value, "fun main() {\n\n    ", DiffInterval(0, 18), DiffInterval(0, 18)),
            DiffResult(DiffTag.DELETION.value,
                       "// You already are within the body of func main()\n    // Declare and assign the correct value to the 'chest' variable below:",
                       DiffInterval(18, 142), DiffInterval(18, 18)),
            DiffResult(DiffTag.ADDITION.value, "var chest = \"gold\"", DiffInterval(142, 142), DiffInterval(18, 36)),
            DiffResult(DiffTag.EQUAL.value, "\n\n    println(chest)\n}", DiffInterval(142, 164), DiffInterval(36, 58)),
        ]
    ),

    (
        [
            "fun main() {\n\n",
            "    // You already are within the body of func main()\n",
            "    // Declare and assign the correct value to the 'chest' variable below:\n\n",
            "    println(chest)\n"
            "}",
        ],
        [
            "fun main() {\n\n",
            "    // You already are within the body of func main()\n",
            "    // Declare and assign the correct value to the 'chect' variable below:\n\n",
            "    println(chest)\n"
            "}",
        ],
        [
            DiffResult(DiffTag.EQUAL.value,
                       "fun main() {\n\n    // You already are within the body of func main()\n    // Declare and assign the correct value to the 'che",
                       DiffInterval(0, 123), DiffInterval(0, 123)),
            DiffResult(DiffTag.DELETION.value, "s", DiffInterval(123, 124), DiffInterval(123, 123)),
            DiffResult(DiffTag.ADDITION.value, "c", DiffInterval(124, 124), DiffInterval(123, 124)),
            DiffResult(DiffTag.EQUAL.value, "t' variable below:\n\n    println(chest)\n}", DiffInterval(124, 164),
                       DiffInterval(124, 164)),
        ]
    ),

    (
        [
            "fun main() {\n\n",
            "    // You already are within the body of func main()\n",
            "    // Declare and assign the correct value to the 'chest' variable below:\n\n",
            "    println(chest)\n"
            "}",
        ],
        [
            "fun main() {\n\n",
            "    // You already are within the body of func main()\n",
            "    // Declare and assign the correct value to the 'chect' variable below:\n\n",
            "    var chest = \"gold\"\n\n",
            "    println(chest)\n"
            "}",
        ],
        [
            DiffResult(DiffTag.EQUAL.value,
                       "fun main() {\n\n    // You already are within the body of func main()\n    // Declare and assign the correct value to the 'che",
                       DiffInterval(0, 123), DiffInterval(0, 123)),
            DiffResult(DiffTag.DELETION.value, "s", DiffInterval(123, 124), DiffInterval(123, 123)),
            DiffResult(DiffTag.ADDITION.value, "c", DiffInterval(124, 124), DiffInterval(123, 124)),
            DiffResult(DiffTag.EQUAL.value, "t' variable below:\n\n", DiffInterval(124, 144), DiffInterval(124, 144)),
            DiffResult(DiffTag.ADDITION.value, "    var chest = \"gold\"\n\n", DiffInterval(144, 144),
                       DiffInterval(144, 168)),
            DiffResult(DiffTag.EQUAL.value, "    println(chest)\n}", DiffInterval(144, 164), DiffInterval(168, 188)),
        ]
    ),
]
