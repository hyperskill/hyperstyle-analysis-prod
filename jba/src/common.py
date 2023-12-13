from typing import List

import pandas as pd

from jba.src.models.edu_columns import EduColumnName


def get_edu_name_columns(df: pd.DataFrame) -> List[str]:
    df_columns = df.columns.tolist()

    edu_name_columns = [
        EduColumnName.SECTION_NAME.value,
        EduColumnName.LESSON_NAME.value,
        EduColumnName.TASK_NAME.value,
    ]

    return [element for element in edu_name_columns if element in df_columns]
