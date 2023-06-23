# Hyperstyle evaluation

This module allows running the [Hyperstyle](https://github.com/hyperskill/hyperstyle/blob/main/README.md) tool on a `xlsx` or `csv` table to get code quality for all code fragments. 
The dataset must contain at least four columns: 
- `id` - is a unique solution number
- `step_id` - is a step id
- `code` - solution code
- `lang`- language in which the code is written in the `code` column. Must belong to one of the following values: `java7`, `java8`, `java9`, `java11`, `java15`, `java17`, `python3`.

Output file is a new `xlsx` or `csv` file with the all columns from the input file and two additional ones:
- `hyperstyle_issues` - json string with full traceback of [hyperstyle](https://github.com/hyperskill/hyperstyle/blob/main/README.md) code quality analysis tool.
- `code_style_feedback_time` - time in seconds that was spent to evaluate this submission.

## Usage

Run the [evaluate.py](evaluate.py) with the arguments from command line.

Required arguments:

`solutions_file_path` — path to xlsx-file or csv-file with code samples to inspect.

Optional arguments:

| Argument                                                  | Description                                                                                                                          |
|-----------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| **&#8209;tp**, **&#8209;&#8209;tool&#8209;path**          | Path to the hyperstyle tool.                                                                                                         |
| **&#8209;o**, **&#8209;&#8209;output&#8209;path**         | Path to the directory where to save evaluation results. Use parent directory of `solutions_file_path` if not specified.              |
| **&#8209;venv**, **&#8209;&#8209;venv**                   | Path to venv to run the tool to get Python for running the tool.                                                                     |
| **&#8209;cwd**, **&#8209;&#8209;working&#8209;directory** | Path to the working directory with the tool.                                                                                         |
| **&#8209;td**, **&#8209;&#8209;tmp&#8209;directory**      | Path to the directory where to save temporary created files results. Use default if not specified.                                   |
| **&#8209;&#8209;allow&#8209;duplicates**                  | Allow duplicate issues found by different linters. By default, duplicates are skipped.                                               |
| **&#8209;&#8209;with&#8209;all&#8209;categories**         | Without this flag, all issues will be categorized into 5 main categories: CODE_STYLE, BEST_PRACTICES, ERROR_PRONE, COMPLEXITY, INFO. |
| **&#8209;d**, **&#8209;&#8209;disable**                   | Disable inspectors, example: pylint,flake8.                                                                                          |

### From Paddle

The [Paddle](https://github.com/JetBrains-Research/paddle#tasks-section) build system, you can use it to run this script:
- add arguments to the `run_hyperstyle` task in the [paddle.yaml](./../../../paddle.yaml) file:

```yaml
    - id: run_hyperstyle
      entrypoint: data_labelling/hyperstyle/evaluate.py
      args:
        - path-to-submissions
        - --output-path path-to-output
        - --disable pylint,flake8,radon
        - -cwd path-to-working-directory
        - --tool-path path-to-hyperstyle
        - --venv path-to-venv
        - --with-all-categories
```
Next you just need to run this task.
