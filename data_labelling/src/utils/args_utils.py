from enum import Enum, unique

from core.src.model.column_name import SubmissionColumns
from core.src.utils.file.extension_utils import AnalysisExtension

from hyperstyle.src.python.common.tool_arguments import ArgumentsInfo
from hyperstyle.src.python.review.application_config import LanguageVersion


@unique
class EvaluationArgument(Enum):
    TRACEBACK = 'traceback'
    RESULT_FILE_NAME = 'evaluation_results'
    RESULT_FILE_NAME_XLSX = f'{RESULT_FILE_NAME}{AnalysisExtension.XLSX.value}'
    RESULT_FILE_NAME_CSV = f'{RESULT_FILE_NAME}{AnalysisExtension.CSV.value}'


@unique
class EvaluationRunToolArgument(Enum):
    SOLUTIONS_FILE_PATH = ArgumentsInfo(
        None,
        'solutions_file_path',
        'Local XLSX-file or CSV-file path. '
        'Your file must include column-names: '
        f'"{SubmissionColumns.CODE.value}" and '
        f'"{SubmissionColumns.LANG.value}". Acceptable values for '
        f'"{SubmissionColumns.LANG.value}" column are: '
        f'{LanguageVersion.PYTHON_3.value}, {LanguageVersion.JAVA_8.value}, '
        f'{LanguageVersion.JAVA_11.value}, {LanguageVersion.KOTLIN.value}.',
    )

    DIFFS_FILE_PATH = ArgumentsInfo(
        None,
        'diffs_file_path',
        'Path to a file with serialized diffs that were founded by diffs_between_df.py',
    )

    INSPECTIONS_PATH = ArgumentsInfo(None, 'inspections_path', 'Path to a CSV file with inspections list.')

    DUPLICATES = ArgumentsInfo(None, '--remove-duplicates', 'Remove duplicates around inspections')


script_structure_rule = (
    'Please, make sure your XLSX-file matches following script standards: \n'
    '1. Your XLSX-file or CSV-file should have 2 obligatory columns named:'
    f'"{SubmissionColumns.CODE.value}" & "{SubmissionColumns.LANG.value}". \n'
    f'"{SubmissionColumns.CODE.value}" column -- relates to the code-sample. \n'
    f'"{SubmissionColumns.LANG.value}" column -- relates to the language of a '
    'particular code-sample. \n'
    '2. Your code samples should belong to the one of the supported languages. \n'
    'Supported languages are: Java, Kotlin, Python. \n'
    f'3. Check that "{SubmissionColumns.LANG.value}" column cells are filled with '
    'acceptable language-names: \n'
    f'Acceptable language-names are: {LanguageVersion.PYTHON_3.value}, '
    f'{LanguageVersion.JAVA_8.value} ,'
    f'{LanguageVersion.JAVA_11.value} and {LanguageVersion.KOTLIN.value}.'
)
