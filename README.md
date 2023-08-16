# Hyperstyle analysis

This repository contains several tools-helpers to work with data from the Hyperstyle platform:

- [core](./core) module contains some common functions like pandas utilities or some common models
- [templates](./templates/README.md) module contains algorithms for searching code quality issues in the pre-written templates.
- [data collection](./data_collection/README.md) module contains client for Hyperskill. This module use platforms' APIs to extract information about following entities from the educational platforms.
- [preprocessing](./preprocessing/README.md) module contains methods to preprocess and prepare data, collected from Hyperskill educational platform, for further analysis.

### JetBrains Academy/Hyperskill platform

On the JetBrains Academy platform, the educational process is structured as follows: firstly,
the student’s solution is checked for correctness using traditional predefined tests. Then, two
scenarios are possible:

**(1)** if the solution is incorrect (contains compilation errors or does not pass all tests), 
then these problems are reported to the student, and they continue to solve the
task;

**(2)** if the solution is correct, the [Hyperstyle](https://github.com/hyperskill/hyperstyle) tool is launched to check the quality of the code.


Therefore, the result of the Hyperstyle tool can only be determined for _correct_ solutions,
that is, solutions that pass all tests. After successfully passing the solution, the student receives
a code quality grade on a four-point scale, and all detected issues (if any) are highlighted in
the code editor. An example of the Hyperstyle user interface:

![The Hyperstyle user interface on the JetBrains Academy platform.](./images/hyperstyle.png "The Hyperstyle user interface on the JetBrains Academy platform.")


## Getting started

### Run via poetry

This project uses the [Poetry](https://github.com/python-poetry/poetry) build system. To set up everything you need:
1. [Install](https://python-poetry.org/docs/#installation) poetry.
2. Clone this repository
3. Run `poetry install --with <list_of_optional_modules>`, where `<list_of_optional_modules>` is a list of modules what you need to install. Only the [`core`](core) module is not an optional and is always installed.
   For example, if you want to install the [`data_collection`](data_collection), [`jba`](jba) and [`preprocessing`](preprocessing) modules, then you should run `poetry install --with data-collection,jba,preporcessing`.

To run any script in the repository just execute:
```bash
poetry run python /path/to/the/script.py [script_arguments]
```

There are also several aliases for main scripts. 
You could find them inside the [pyproject.toml](pyproject.toml) file in the `[tool.poetry.scripts]` section. 
To run any script using its alias just execute:
```bash
poetry run <script_alias> [script_arguments]
```

### Run via Docker

If you don't want to install poetry, you could use our official Docker image where all necessary environment is installed. 
To do this:
1. Pull the image:
   ```bash
   docker pull registry.jetbrains.team/p/code-quality-for-online-learning-platforms/hyperstyle-analysis-prod/hyperstyle-analysis-prod:<VERSION>
   ```
   where `<VERSION>` is the project version you would like to use. You could always find the latest version inside the [pyproject.toml](pyproject.toml) file.

2. Run a container with the command you would like to execute.
   ```bash
   docker run hyperstyle-analysis-prod:<VERSION> <command>
   ```
   For example:
   ```bash
   docker run hyperstyle-analysis-prod:<VERSION> poetry run <script_alias> [script_arguments]
   ```
