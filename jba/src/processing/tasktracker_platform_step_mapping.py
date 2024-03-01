import argparse
import ast
from pathlib import Path

import pandas as pd

from core.src.utils.df_utils import read_df, filter_df_by_single_value, write_df
from jba.src.models.edu_columns import EduTaskStatus, EduColumnName

pd.options.mode.chained_assignment = None

PACKAGE_TO_LESSON_NUMBER = {
    'jetbrains.kotlin.course.welcome': 1,
    'jetbrains.kotlin.course.first.date': 2,
    'jetbrains.kotlin.course.chat': 3,
    'jetbrains.kotlin.course.warmup': 4,
    'jetbrains.kotlin.course.mastermind.advanced': 5,
    'jetbrains.kotlin.course.hangman': 6,
    'jetbrains.kotlin.course.almost.done': 7,
    'jetbrains.kotlin.course.last.push': 8,
}

# Platform column names
SOLUTION_TEXT = 'solution_text'
EMAIL = 'email'

# TaskTracker column names
TASKTRACKER_DATE = 'date'
TASKTRACKER_FRAGMENT = 'fragment'
TASKTRACKER_EMAIL = 'email'
TASKTRACKER_PACKAGE = 'task'
TASKTRACKER_TASK_NAME = EduColumnName.TASK_NAME.value
TASKTRACKER_LESSON_NUMBER = EduColumnName.LESSON_NUMBER.value

# Output file name
OUTPUT_FILENAME = 'tasktracker_data_mapped.csv'


def find_mapping_solutions(user_df: pd.DataFrame, platform_df: pd.DataFrame, lesson: int) -> pd.DataFrame:
    user_ind, platform_ind = 0, 0
    user_index = list(user_df.index)
    platform_task_name = None
    last_status = EduTaskStatus.CORRECT.value

    user_df[TASKTRACKER_LESSON_NUMBER] = lesson
    user_df[TASKTRACKER_TASK_NAME] = None

    for platform_ind in platform_df.index:
        platform_solution = _get_sent_solution(platform_df.loc[platform_ind])
        platform_datetime = platform_df.at[platform_ind, EduColumnName.SUBMISSION_DATETIME.value]
        platform_task_name = platform_df.at[platform_ind, EduColumnName.TASK_NAME.value]

        while user_ind < len(user_df) and user_df.at[user_index[user_ind], TASKTRACKER_DATE] < platform_datetime:
            last_status = platform_df.at[platform_ind, EduColumnName.STATUS.value]
            exact_match = user_df.at[user_index[user_ind], TASKTRACKER_FRAGMENT] == platform_solution
            user_df.at[user_index[user_ind], TASKTRACKER_TASK_NAME] = platform_task_name
            user_ind += 1

            if exact_match:
                break

        if user_ind == len(user_df):
            break

    if last_status == EduTaskStatus.WRONG.value:
        for index, _ in enumerate(range(user_ind, len(user_df))):
            user_df.at[user_index[index + user_ind], TASKTRACKER_TASK_NAME] = platform_task_name

    return user_df


def _get_sent_solution(platform_record: pd.Series) -> str | None:
    try:
        return list(ast.literal_eval(platform_record[SOLUTION_TEXT]).values())[0]
    except SyntaxError:
        return None


def map_solutions(tasktracker_file_path: Path, platform_file_path: Path) -> pd.DataFrame:
    tasktracker_df = read_df(tasktracker_file_path)
    platform_df = read_df(platform_file_path)

    tasktracker_df = tasktracker_df.dropna(
        subset=[TASKTRACKER_DATE, TASKTRACKER_FRAGMENT, TASKTRACKER_EMAIL, TASKTRACKER_PACKAGE])

    tasktracker_df = tasktracker_df.sort_values(by=TASKTRACKER_DATE)
    platform_df = platform_df.sort_values(by=EduColumnName.SUBMISSION_DATETIME.value)

    tasktracker_df[TASKTRACKER_LESSON_NUMBER] = None
    tasktracker_df[TASKTRACKER_TASK_NAME] = None

    user_emails = tasktracker_df[TASKTRACKER_EMAIL].unique()

    for user in user_emails:
        user_tasktracker_df = filter_df_by_single_value(tasktracker_df, TASKTRACKER_EMAIL, user)
        user_platform_df = filter_df_by_single_value(platform_df, EMAIL, user)
        lessons = user_tasktracker_df[TASKTRACKER_PACKAGE].unique()

        for lesson in lessons:
            lesson_number = PACKAGE_TO_LESSON_NUMBER[lesson]
            user_tasktracker_filtered_df = filter_df_by_single_value(user_tasktracker_df, TASKTRACKER_PACKAGE, lesson)
            user_platform_filtered_df = filter_df_by_single_value(user_platform_df, EduColumnName.LESSON_NUMBER.value,
                                                                  lesson_number)

            user_tasktracker_filtered_df = find_mapping_solutions(user_tasktracker_filtered_df,
                                                                  user_platform_filtered_df, lesson_number)
            tasktracker_df.loc[
                user_tasktracker_filtered_df.index,
                [TASKTRACKER_LESSON_NUMBER, TASKTRACKER_TASK_NAME]
            ] = user_tasktracker_filtered_df[[TASKTRACKER_LESSON_NUMBER, TASKTRACKER_TASK_NAME]]

    return tasktracker_df


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "tasktracker_file_path",
        type=lambda value: Path(value).absolute(),
        help="Path to .csv file with TaskTracker dataset."
    )
    parser.add_argument(
        "platform_file_path",
        type=lambda value: Path(value).absolute(),
        help="Path to .csv file with platform dataset."
    )
    parser.add_argument(
        "output_path",
        type=lambda value: Path(value).absolute(),
        help="Path to output directory."
    )


def main():
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args()

    result_df = map_solutions(args.tasktracker_file_path, args.platform_file_path)
    write_df(result_df, args.output_path / OUTPUT_FILENAME)


if __name__ == '__main__':
    main()
