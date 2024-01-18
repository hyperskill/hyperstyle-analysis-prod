from enum import Enum, unique

import pandas as pd
import streamlit as st

from core.src.utils.df_utils import read_df
from jba.src.visualization.common.utils import read_submissions
from jba.src.visualization.common.widgets import show_submission_postprocess_filters
from jba.src.visualization.pages.automated_analysis.failed_users_analysis import show_failed_users_analysis
from jba.src.visualization.pages.automated_analysis.median_attempts_analysis import show_median_attempts_analysis
from jba.src.visualization.pages.automated_analysis.median_test_attempts_analysis import show_test_attempts_analysis


@unique
class Analysis(Enum):
    BY_MEDIAN_ATTEMPTS = 'By median attempts'
    BY_FAILED_USERS = 'By failed users'
    BY_MEDIAN_TEST_ATTEMPTS = 'By median test attempts'

    def run(self, submissions: pd.DataFrame, course_structure: pd.DataFrame):
        analysis_to_main_function = {
            Analysis.BY_MEDIAN_ATTEMPTS: show_median_attempts_analysis,
            Analysis.BY_FAILED_USERS: show_failed_users_analysis,
            Analysis.BY_MEDIAN_TEST_ATTEMPTS: show_test_attempts_analysis,
        }

        return analysis_to_main_function[self](submissions, course_structure)


def main():
    with st.sidebar:
        analysis = st.selectbox('Analysis:', options=Analysis, format_func=lambda item: item.value)

    filters = show_submission_postprocess_filters()
    submissions = read_submissions(st.session_state.submissions_path, filters)
    course_structure = read_df(st.session_state.course_structure_path)

    analysis.run(submissions, course_structure)


if __name__ == '__main__':
    main()
