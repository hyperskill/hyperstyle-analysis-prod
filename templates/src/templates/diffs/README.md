## Filtering based on difference analysis of code from template and students code

The idea of this algorithm is to build diff between template and students code and consider issue as template if 
it places in code with zero difference from template.

We use [diff-match-patch](https://github.com/google/diff-match-patch) library to find diff between code. 
The example of input and output is following:

```python
template = "x = 1\ny = # your code here\nprint(x, y)"
code = "x = 1\ny = 2\nprint(x, y)"

dmp = diff_match_patch.diff_match_patch()
diff = dmp.diff_main(template, code)
# Result: [(0, "x = 1\ny = "), (-1, "# your code here"), (1, "2"), (0, "\nprint(x, y)")]
```
The result is array of pairs: tag (-1 - deletion, 0 - equal, 1 - addition) and the code substring.
So is issue position falls into code substring with tag 1 (new code added by student) it can be considered as student code issue,
otherwise if  with tag 0 (code is identical to template) it is considered as template issue. 
Deleted parts from template are not considered as they are not presented in code => no information about issues inside them.

As the position of issue is defined as line number + column number, we need to recalculate them considering code as single line test:
```python
x = int(input())
if x == 5:
    print('hello') # MagicNumber line_number=3 column_number=9
```

```python
code = "x = int(input())\nif x == 5:\n\tprint('hello')" # MagicNumber offset=27
```

### Usage

Run the [filter_by_diff.py](filter_by_diff.py) script with the arguments from command line.

Required arguments:

- `submissions_path` — Path to .csv file with submissions. The file must contain the following columns: `id`, `lang`, `step_id`, `code`, `group`, `attempt`, `hyperskill_issues`/`qodana_issues` (please, use [preprocess_submissions.py](../preprocessing/preprocess_submissions.py) script to get  `group` and `attempt` columns).
- `steps_path` — Path to .csv file with steps. The file must contain the following columns: `id`, and `code_template` OR `code_templates`.
- `issues_column` — Column name in .csv file with submissions where issues are stored (can be `hyperstyle_issues` ot `qodana_issues`).

Optional arguments:

- `--output-path` — Path to resulting .csv file with submissions with filtered issues. If no value was passed, the output will be printed into the console.
- `--log-path` — Path to directory for log. The default value is `None`.

### Output format
Output csv file will be saved to `filtered_submissions_path` and will contain all data from csv in `submissions_path` but issues from `issues_column` will be modified in following way:
- `issues_column` will contain only students issues with filtered template issues
- `issues_column` + `_diff` will contain filtered template issues
- `issues_column` + `_all` will contain both students and template issues
- `issues_column` + `_diff_template_positions` - for each issue from the `issues_column` + `_diff` column stores row number and offset in this row in the template.

