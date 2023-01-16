from src.templates.diffs.model.diff_interval import DiffInterval
from src.templates.diffs.model.diff_result import DiffResult
from src.templates.diffs.model.diff_tag import DiffTag

DIFF_TEST_DATA_JAVA = [
    (
        [
            "public class Main {\n",
            "    public static void main(String args[]) {\n",
            "        int a = 1;\n",
            "        int b = 2;\n",
            "        int c = // put your code here\n",
            "        System.out.println(a, b, c);\n"
            "    }\n",
            "}"
        ],
        [
            "public class Main {\n",
            "    public static void main(String args[]) {\n",
            "        int a = 1;\n",
            "        int b = 2;\n",
            "        int c = 3;\n",
            "        System.out.println(a, b, c);\n"
            "    }\n",
            "}"
        ],
        [
            DiffResult(DiffTag.EQUAL.value,
                       "public class Main {\n    public static void main(String args[]) {\n        int a = 1;\n        int b = 2;\n        int c = ",
                       DiffInterval(0, 119), DiffInterval(0, 119)),
            DiffResult(DiffTag.DELETION.value, "// put your code here", DiffInterval(119, 140), DiffInterval(119, 119)),
            DiffResult(DiffTag.ADDITION.value, "3;", DiffInterval(140, 140), DiffInterval(119, 121)),
            DiffResult(DiffTag.EQUAL.value, "\n        System.out.println(a, b, c);\n    }\n}", DiffInterval(140, 185),
                       DiffInterval(121, 166))
        ]
    ),

    (
        [
            "public class Main {\n",
            "    public static void main(String args[]) {\n",
            "        int a = 1;\n",
            "        int b = 2;\n",
            "        int c = // put your code here\n",
            "        System.out.println(a, b, c);\n"
            "    }\n",
            "}"
        ],
        [
            "public class Main {\n",
            "    public static void main(String args[]) {\n",
            "        int A = 1;\n",
            "        int b = 2;\n",
            "        int c = 3;\n",
            "        System.out.println(a, b, c);\n"
            "    }\n",
            "}"
        ],
        [
            DiffResult(DiffTag.EQUAL.value,
                       "public class Main {\n    public static void main(String args[]) {\n        int ",
                       DiffInterval(0, 77), DiffInterval(0, 77)),
            DiffResult(DiffTag.DELETION.value, "a", DiffInterval(77, 78), DiffInterval(77, 77)),
            DiffResult(DiffTag.ADDITION.value, "A", DiffInterval(78, 78), DiffInterval(77, 78)),
            DiffResult(DiffTag.EQUAL.value, " = 1;\n        int b = 2;\n        int c = ",
                       DiffInterval(78, 119), DiffInterval(78, 119)),
            DiffResult(DiffTag.DELETION.value, "// put your code here", DiffInterval(119, 140), DiffInterval(119, 119)),
            DiffResult(DiffTag.ADDITION.value, "3;", DiffInterval(140, 140), DiffInterval(119, 121)),
            DiffResult(DiffTag.EQUAL.value, "\n        System.out.println(a, b, c);\n    }\n}", DiffInterval(140, 185),
                       DiffInterval(121, 166))
        ]
    ),

    (
        [
            "public class Main {\n",
            "    public static void main(String args[]) {\n",
            "        int a = 1;\n",
            "        int b = 2;\n",
            "        int c = 3;\n",
            "    }\n",
            "}"
        ],
        [
            "public class Main {\n",
            "    public static void main(String args[]) {\n",
            "        int b = 2;\n",
            "        int a = 1;\n",
            "        int c = 3;\n",
            "    }\n",
            "}"
        ],
        # Lines swap does not work properly
        [
            DiffResult(DiffTag.EQUAL.value,
                       "public class Main {\n    public static void main(String args[]) {\n        int ",
                       DiffInterval(0, 77), DiffInterval(0, 77)),
            DiffResult(DiffTag.DELETION.value, "a", DiffInterval(77, 78), DiffInterval(77, 77)),
            DiffResult(DiffTag.ADDITION.value, "b", DiffInterval(78, 78), DiffInterval(77, 78)),
            DiffResult(DiffTag.EQUAL.value, " = ", DiffInterval(78, 81), DiffInterval(78, 81)),

            DiffResult(DiffTag.DELETION.value, "1", DiffInterval(81, 82), DiffInterval(81, 81)),
            DiffResult(DiffTag.ADDITION.value, "2", DiffInterval(82, 82), DiffInterval(81, 82)),
            DiffResult(DiffTag.EQUAL.value, ";\n        int ", DiffInterval(82, 96), DiffInterval(82, 96)),

            DiffResult(DiffTag.DELETION.value, "b", DiffInterval(96, 97), DiffInterval(96, 96)),
            DiffResult(DiffTag.ADDITION.value, "a", DiffInterval(97, 97), DiffInterval(96, 97)),
            DiffResult(DiffTag.EQUAL.value, " = ", DiffInterval(97, 100), DiffInterval(97, 100)),

            DiffResult(DiffTag.DELETION.value, "2", DiffInterval(100, 101), DiffInterval(100, 100)),
            DiffResult(DiffTag.ADDITION.value, "1", DiffInterval(101, 101), DiffInterval(100, 101)),
            DiffResult(DiffTag.EQUAL.value, ";\n        int c = 3;\n    }\n}", DiffInterval(101, 129),
                       DiffInterval(101, 129)),
        ]
    ),
    (
        [
            "public class Main {\n",
            "    public static void main(String args[]) {\n\n",
            "        // You already are within the body of func main()\n",
            "        // Declare and assign the correct value to the 'varchest' variable below:\n\n",
            "        System.out.println(varchest);\n"
            "    }\n",
            "}"
        ],
        [
            "public class Main {\n",
            "    public static void main(String args[]) {\n\n",
            "        String varchest = \"gold\";\n\n",
            "        System.out.println(varchest);\n"
            "    }\n",
            "}"
        ],
        [
            DiffResult(DiffTag.EQUAL.value,
                       "public class Main {\n    public static void main(String args[]) {\n\n        ",
                       DiffInterval(0, 74), DiffInterval(0, 74)),
            DiffResult(DiffTag.DELETION.value,
                       "// You already are within the body of func main()\n        // Declare and assign the correct value to the 'varchest' variable below:",
                       DiffInterval(74, 205), DiffInterval(74, 74)),
            DiffResult(DiffTag.ADDITION.value, "String varchest = \"gold\";", DiffInterval(205, 205),
                       DiffInterval(74, 99)),
            DiffResult(DiffTag.EQUAL.value, "\n\n        System.out.println(varchest);\n    }\n}",
                       DiffInterval(205, 252), DiffInterval(99, 146)),
        ]
    ),

    (
        [
            "public class Main {\n",
            "    public static void main(String args[]) {\n\n",
            "        // You already are within the body of func main()\n",
            "        // Declare and assign the correct value to the 'varchest' variable below:\n\n",
            "        System.out.println(varchest);\n"
            "    }\n",
            "}"
        ],
        [
            "public class Main {\n",
            "    public static void main(String args[]) {\n\n",
            "        // You already are within the body of func main()\n",
            "        // Declare and assign the correct value to the 'valchest' variable below:\n\n",
            "        System.out.println(varchest);\n"
            "    }\n",
            "}"
        ],
        [
            DiffResult(DiffTag.EQUAL.value,
                       "public class Main {\n    public static void main(String args[]) {\n\n        // You already are within the body of func main()\n        // Declare and assign the correct value to the 'va",
                       DiffInterval(0, 182), DiffInterval(0, 182)),
            DiffResult(DiffTag.DELETION.value, "r", DiffInterval(182, 183), DiffInterval(182, 182)),
            DiffResult(DiffTag.ADDITION.value, "l", DiffInterval(183, 183), DiffInterval(182, 183)),
            DiffResult(DiffTag.EQUAL.value, "chest' variable below:\n\n        System.out.println(varchest);\n    }\n}",
                       DiffInterval(183, 252), DiffInterval(183, 252)),
        ]
    ),

    (
        [
            "public class Main {\n",
            "    public static void main(String args[]) {\n\n",
            "        // You already are within the body of func main()\n",
            "        // Declare and assign the correct value to the 'varchest' variable below:\n\n",
            "        System.out.println(varchest);\n"
            "    }\n",
            "}"
        ],
        [
            "public class Main {\n",
            "    public static void main(String args[]) {\n\n",
            "        // You already are within the body of func main()\n",
            "        // Declare and assign the correct value to the 'valchest' variable below:\n\n",
            "        String varchest = \"gold\";\n\n",
            "        System.out.println(varchest);\n"
            "    }\n",
            "}"
        ],
        [
            DiffResult(DiffTag.EQUAL.value,
                       "public class Main {\n    public static void main(String args[]) {\n\n        // You already are within the body of func main()\n        // Declare and assign the correct value to the 'va",
                       DiffInterval(0, 182), DiffInterval(0, 182)),
            DiffResult(DiffTag.DELETION.value, "r", DiffInterval(182, 183), DiffInterval(182, 182)),
            DiffResult(DiffTag.ADDITION.value, "l", DiffInterval(183, 183), DiffInterval(182, 183)),
            DiffResult(DiffTag.EQUAL.value, "chest' variable below:\n\n",
                       DiffInterval(183, 207), DiffInterval(183, 207)),
            DiffResult(DiffTag.ADDITION.value, "        String varchest = \"gold\";\n\n",
                       DiffInterval(207, 207), DiffInterval(207, 242)),
            DiffResult(DiffTag.EQUAL.value, "        System.out.println(varchest);\n    }\n}",
                       DiffInterval(207, 252), DiffInterval(242, 287)),
        ]
    ),
]
