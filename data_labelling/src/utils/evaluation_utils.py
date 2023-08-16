import logging
from pathlib import Path
from typing import Callable, List, TypeVar, Optional, Tuple

import pandas as pd
import time

from core.src.model.column_name import SubmissionColumns
from core.src.utils.file.file_utils import create_directory, remove_directory, create_file
from core.src.utils.file.saving_utils import save_solution_to_file
from core.src.utils.quality.report_utils import get_language_version
from core.src.utils.subprocess_runner import run_in_subprocess
from data_labelling.src.utils.evaluation_config import EvaluationConfig

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

T = TypeVar('T')


def evaluate_by_solution(df_solutions: pd.DataFrame,
                         config: EvaluationConfig,
                         parse_result: Callable[[Path], pd.Series],
                         working_directory: Optional[str] = None) -> pd.DataFrame:
    """
    Run evaluation tool on each solution separately.
    Return solutions with evaluation results.
    """

    results = df_solutions.apply(
        lambda solution: evaluate(solution, config, parse_result, working_directory=working_directory),
        axis=1
    )
    feedback_df = pd.DataFrame.from_records(results,
                                            columns=[SubmissionColumns.HYPERSTYLE_ISSUES.value,
                                                     SubmissionColumns.CODE_STYLE_FEEDBACK_TIME.value])
    return pd.concat([df_solutions, feedback_df], axis=1)


def evaluate(
        solution: pd.Series,
        config: EvaluationConfig,
        parse_result: [[Path], T],
        working_directory: Optional[str] = None
) -> Tuple[T, float]:
    """
    Run tool on directory with group of solutions written on same language version.
    Return path to evaluation result.
    """
    language_version = solution[SubmissionColumns.LANG.value]

    language_version_path = create_directory(config.tmp_path / language_version, clear=True)
    input_path = create_directory(language_version_path / 'input', clear=True)
    output_path = create_directory(language_version_path / 'output', clear=True)

    submission_path = save_solution_to_file(solution, input_path)
    command = config.build_command(input_path, output_path, get_language_version(language_version), submission_path)
    output, cur_time = evaluate_command(command, working_directory)
    if output is not None:
        next(create_file(output_path / config.result_path, output))

    result = parse_result(output_path / config.result_path)[0]

    remove_directory(language_version_path)

    return result, cur_time


def evaluate_command(command: List[str], working_directory: Optional[str] = None) -> Tuple[Optional[str], float]:
    logger.info('Start evaluation')
    start = time.time()

    logger.info(f'Executing command: {" ".join(command)}')
    output, _ = run_in_subprocess(command, working_directory=working_directory)

    end = time.time()
    logger.info(f'Finish evaluation time={end - start}s')
    return output, end - start
