# Hyperskill/JetBrains Academy data preprocessing

This module contains methods to preprocess and prepare data, collected from JetBrains Academy/Hyperskill educational platform, 
for further analysis.
More information about the platform and the use of Hyperstyle can be found [here](./README.md).

## 1. Preprocess submissions

### Usage

Execute one of the following commands with necessary arguments:
```bash
poetry run preprocess_submissions [arguments]
```
or
```bash
docker run hyperstyle-analysis-prod:<VERSION> poetry run preprocess_submissions [arguments]
```

**Required arguments:**
    
| Argument                           | Description                                                                                                                                                                               |
|------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **submissions_path**               | Path to .csv file with `submissions`. The file must contain the following columns: `id`, `step` (or `step_id`), `code`, `user_id`, `time`. The following columns are optional: `client`.  |
| **preprocessed_submissions_path**  | Path to .csv output file with `preprocessed submissions` with issues. If not provided the output will be printed into console.                                                            |



**Optional arguments:**
    
| Argument                                     | Description                                                                                                          |
|----------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| **--users-to-submissions-path**              | Path to file with `user` to submission relation (if data is not presented in submissions dataset or was anonymized). |
| **--diff-ratio**                             | Ration to remove submissions which has lines change more then in `diff-ratio` times. Default is 10.0.                |
| **--max-attempts**                           | Remove submissions series with more then `max-attempts` attempts. Default is 5.                                      |

### Output format
Output csv file will be saved to `preprocessed_submissions_path` and will contain all data from csv in `submissions_path` and several additional columns:
- `group` - the number of group in the all students submissions sequences, starts from 0;
- `attempt` - the number of attempt in the current group, starts from 0;
- `total_attempts` - the number of total attempts in the current group.

An example of `preprocessed_submissions_path` can be found in the [tests](tests/resources/preprocessed_submissions_expected.csv):

| id  | step_id | code                                                                 | group | attempt  | total_attempts |
|-----|---------|----------------------------------------------------------------------|-------|----------|----------------|
| 1   | 1       | e = 2.718281828459045 #  put your python code here print('%.5f' % e) | 0     | 1        | 3              |
| 2   | 1       | e = 2.718281828459045 # put your python code here print('%.5f' % e)  | 0     | 2        | 3              |
| ... | ...     | ...                                                                  | ...   | ...      | ...            |
