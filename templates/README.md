## Description

This module contains several algorithms to find code quality issues in pre-written code templates.

The algorithms have been tested on the JetBrains Academy platform. 
As a tool for evaluating code quality, [Hyperstyle](https://github.com/hyperskill/hyperstyle) was used, which is currently used on the platform by default. 
More information about the platform and the use of Hyperstyle can be found [here](./README.md).

# Searching code quality issues in the task templates

This module allows running the algorithm of searching code quality issues 
in the task pre-written templates:

- [an algorithm, based on the diffs analysis](src/diffs/README.md)
- [an algorithm, based on the frequency analysis](src/freq/README.md)

Nowadays, many MOOC platforms use predefined templates in their tasks. For example, on
the [JetBrains Academy](https://www.jetbrains.com/academy/) platform developed by JetBrains, 
the Java language track contains templates in all tasks. 
Another platform — [Khan Academy](https://www.khanacademy.org/) — has many programming tasks
in JavaScript, and almost all programming assignments have pre-written code templates that
the students have to modify. Platforms aimed at more experienced programmers, such as [Leetcode](https://leetcode.com/)
, also often leave a pre-written template for solving a problem. 

Consider several examples of the pre-written templates from the different platforms:

![Several examples of pre-written templates from a) the Khan Academy platform (in
JavaScript), b) Leetcode (in C++), and c) JetBrains Academy (in Java).](./images/templates_from_different_platforms.png "Several examples of pre-written templates from a) the Khan Academy platform (in
JavaScript), b) Leetcode (in C++), and c) JetBrains Academy (in Java).")

The figure shows that templates can be quite long and contain a part of the logic (JavaScript, code snippet a), as
well as basic ones needed to solve the problem (C and Java, code snippets ++ b and c).