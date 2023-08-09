import argparse
from pathlib import Path

from core.src.utils.file.file_utils import get_tmp_directory
from data_labelling.src.hyperstyle.hyperstyle_evaluation_config import HYPERSTYLE_TOOL_PATH
from data_labelling.src.utils.args_utils import EvaluationRunToolArgument


def configure_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.long_name,
                        type=lambda value: Path(value).absolute(),
                        help=EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.description)

    parser.add_argument('-o', '--output-path',
                        default=None,
                        type=lambda value: Path(value).absolute(),
                        help='Path to the directory where to save evaluation results')

    parser.add_argument('-tp', '--tool-path',
                        default=HYPERSTYLE_TOOL_PATH,
                        type=str,
                        help='Path to script inside docker (or locally) to run on files.')

    parser.add_argument('-venv', '--venv',
                        default=None,
                        type=str,
                        help='Path to venv to run the tool.')

    parser.add_argument('-cwd', '--working-directory',
                        default=None,
                        type=str,
                        help='Path to the working directory with the tool.')

    parser.add_argument('-td', '--tmp-directory',
                        default=get_tmp_directory(),
                        type=lambda value: Path(value).absolute(),
                        help='Path to tmp directory to save temporary files')

    parser.add_argument('--allow-duplicates',
                        help='Allow duplicate issues found by different linters. By default, duplicates are skipped.',
                        action='store_true')

    parser.add_argument('--with-all-categories',
                        help='Without this flag, all issues will be categorized into 5 main categories: '
                             'CODE_STYLE, BEST_PRACTICES, ERROR_PRONE, COMPLEXITY, INFO.',
                        action='store_true')

    parser.add_argument('-d', '--disable',
                        default=None,
                        type=str,
                        help='Disable inspectors, example: pylint,flake8.')
