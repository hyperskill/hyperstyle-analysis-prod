import json
from typing import Optional

import pandas as pd

from core.src.model.column_name import SubmissionColumns
from jba.src.models.edu_columns import EduColumnName, EduTaskStatus


def get_main_content(snippets) -> Optional[str]:
    for snippet in snippets:
        if 'Main.kt' in snippet['name']:
            return '\n' + snippet['text']  # noqa: WPS336

    return None


def convert_submissions(submissions: pd.DataFrame) -> pd.DataFrame:
    # Keeping only the latest successful submissions
    converted_submissions = submissions[submissions[EduColumnName.STATUS.value] == EduTaskStatus.CORRECT.value]
    converted_submissions = converted_submissions.groupby(SubmissionColumns.GROUP.value).tail(1)

    converted_submissions.dropna(subset=[EduColumnName.CODE_SNIPPETS.value], inplace=True)
    converted_submissions[SubmissionColumns.CODE.value] = converted_submissions[
        EduColumnName.CODE_SNIPPETS.value
    ].apply(lambda x: get_main_content(json.loads(x)))

    return converted_submissions
