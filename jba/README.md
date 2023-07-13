## Description

This module contains utilities to analyze data from JetBrains Marketplace.

----

# Preprocess data

This module contains script to preprocess row data to perform further analysis.

1. [prepare_course_data.py](./src/jba/processing/prepare_course_data.py) allows you to filter 
data by the course id and also to collect information about the course structure.

### Usage

Run the script by one of the following way with the arguments:

Required arguments:

- `data_path` — Path to .csv file with collected data. The file must contain the following columns: `task_id`, `course_id`, `submission_datetime`, `status`, `task_type`, `user_id`, `task_name` (see [an example](./tests/resources/jba_tests/processing/all_data.csv) in the tests).
- `course_id` — Course id to analyze.
- `course_sources_path` — Path to course sources to extract course structure (see [an example](./tests/resources/jba_tests/processing/course_example) in the tests).

After this step you will get a new file with `courseId` suffix. This file will contain all data from the `data_path` file, but only for the course with the course id `course_id`.
Also, an additional file with the course structure will be generated, e.g. for the [course](./tests/resources/jba_tests/processing/course_example) from the test folder with the following structure:
```text
- course_root
-- course-info.yaml
-- course-remote-info.yaml
-- section
--- section-info.yaml
--- section-remote-info.yaml
--- lesson
---- lesson-info.yaml
---- lesson-remote-info.yaml
---- task1
----- task-info.yaml
----- task-remote-info.yaml
---- task2
----- task-info.yaml
----- task-remote-info.yaml
```

the [following](./tests/resources/jba_tests/processing/course_1_structure_expected.csv) file will be generated.

2. [data_processing.py](./src/jba/processing/data_processing.py) allows you to process data from the previous step:
- Merge course data with task info
- Add submission group
- Add submission attempt

### Usage

Run the script by one of the following way with the arguments:

Required arguments:

- `course_data_path` — Path to .csv file with preprocessed data by [prepare_course_data.py](./src/jba/processing/prepare_course_data.py).
- `course_structure_path` — Path to .csv file with the course structure gathered by [prepare_course_data.py](./src/jba/processing/prepare_course_data.py).

After this step you will get a new file with course data with `courseId_preprocessed` suffix. 

----

# Analyze data

This module allows you to visualize the data to perform further analysis.

1. [task_solving.py](./src/jba/plots/task_solving.py) allows you to plot line charts how students solve tasks from the course.

Run the script by one of the following way with the arguments:

Required arguments:

- `preprocessed_course_data_path` — Path to .csv file with preprocessed data by [data_processing.py](./src/jba/processing/data_processing.py).
- `course_structure_path` — Path to .csv file with the course structure gathered by [prepare_course_data.py](./src/jba/processing/prepare_course_data.py).

Optional arguments:

| Argument                            | Description                                 |
|-------------------------------------|---------------------------------------------|
| **&#8209;&#8209;course-name**       | Name of the course to display on the chart. |


2. [task_attempt.py](./src/jba/plots/task_attempt.py) allows you to plot line charts how many attempts students spend to solve the tasks from the course.

Run the script by one of the following way with the arguments:

Required arguments:

- `preprocessed_course_data_path` — Path to .csv file with preprocessed data by [data_processing.py](./src/jba/processing/data_processing.py).
- `course_structure_path` — Path to .csv file with the course structure gathered by [prepare_course_data.py](./src/jba/processing/prepare_course_data.py).

Optional arguments:

| Argument                            | Description                                 |
|-------------------------------------|---------------------------------------------|
| **&#8209;&#8209;course-name**       | Name of the course to display on the chart. |

