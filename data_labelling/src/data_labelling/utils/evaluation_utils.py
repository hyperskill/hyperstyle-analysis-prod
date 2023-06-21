import logging
from pathlib import Path
from typing import Callable, List, TypeVar, Optional, Tuple

import pandas as pd
import time

from core.model.column_name import SubmissionColumns
from core.utils.df_utils import merge_dfs
from core.utils.file.file_utils import create_directory, remove_directory, create_file
from core.utils.quality.report_utils import get_language_version
from core.utils.subprocess_runner import run_in_subprocess
from data_labelling.utils.evaluation_config import EvaluationConfig
from data_labelling.utils.file_util import save_solutions_to_files

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def evaluate_by_language(df_solutions: pd.DataFrame,
                         config: EvaluationConfig,
                         parse_result: Callable[[Path], pd.DataFrame],
                         working_directory: Optional[str] = None) -> pd.DataFrame:
    """
    Group solutions by language and run evaluation tool on groups of solutions with same language.
    Return solutions with evaluation results.
    """

    results = []

    for _, df_lang_solutions in df_solutions.groupby(SubmissionColumns.LANG.value):
        result, time = evaluate(df_lang_solutions, config, parse_result, working_directory=working_directory)
        results.append(result)

    df_results = pd.concat(results)
    df_solutions = merge_dfs(df_solutions, df_results,
                             left_on=SubmissionColumns.ID.value,
                             right_on=SubmissionColumns.ID.value,
                             how='left',
                             )
    return df_solutions


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
        lambda solution: evaluate(solution.to_frame().T, config, parse_result, working_directory=working_directory),
        axis=1
    )
    feedback_df = pd.DataFrame.from_records(results,
                                            columns=[SubmissionColumns.HYPERSTYLE_ISSUES.value,
                                                     SubmissionColumns.CODE_STYLE_FEEDBACK_TIME.value])
    return pd.concat([df_solutions, feedback_df], axis=1)


def evaluate(
        df_solutions: pd.DataFrame,
        config: EvaluationConfig,
        parse_result: [[Path], T],
        working_directory: Optional[str] = None
) -> Tuple[T, float]:
    """
    Run tool on directory with group of solutions written on same language version.
    Return path to evaluation result.
    """

    language_versions = df_solutions[SubmissionColumns.LANG.value].apply(get_language_version).unique()
    assert language_versions.size == 1, "Given solution should have same language version"
    language_version = language_versions[0]

    language_version_path = create_directory(config.tmp_path / language_version.value, clear=True)
    input_path = create_directory(language_version_path / 'input', clear=True)
    output_path = create_directory(language_version_path / 'output', clear=True)

    save_solutions_to_files(df_solutions, language_version, input_path, config.with_template)

    command = config.build_command(input_path, output_path, language_version)
    output, time = evaluate_command(command, working_directory)
    if output is not None:
        next(create_file(output_path / config.result_path, output))

    result = parse_result(output_path / config.result_path)

    remove_directory(language_version_path)

    return result, time


def evaluate_command(command: List[str], working_directory: Optional[str] = None) -> Tuple[Optional[str], float]:
    logger.info('Start evaluation')
    start = time.time()

    logger.info('Executing command: ' + (' '.join(command)))
    output, _ = run_in_subprocess(command, working_directory=working_directory)

    end = time.time()
    logger.info(f'Finish evaluation time={end - start}s')
    return output, end - start
