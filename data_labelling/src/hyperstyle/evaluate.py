import argparse
import logging
import sys
import time
from pathlib import Path

import pandas as pd

from core.src.model.column_name import SubmissionColumns
from core.src.model.report.hyperstyle_report import HyperstyleReport
from core.src.utils.df_utils import read_df, write_df
from core.src.utils.file.file_utils import get_output_path, get_output_filename
from data_labelling.src.hyperstyle.evaluation_args import configure_arguments
from data_labelling.src.hyperstyle.hyperstyle_evaluation_config import HyperstyleEvaluationConfig
from data_labelling.src.utils.evaluation_utils import evaluate_by_solution

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

HYPERSTYLE_OUTPUT_SUFFIX = '_hyperstyle'


def parse_hyperstyle_result(results_path: Path) -> pd.Series:
    """ Parse result for single solution. """

    try:
        report = HyperstyleReport.from_file(results_path)
    except Exception as e:
        logging.error(f"Can not parse new format report from hyperstyle output: {e}")
        raise Exception(e)

    return pd.Series({SubmissionColumns.HYPERSTYLE_ISSUES.value: report.to_json()})


def evaluate_hyperstyle(df_solutions: pd.DataFrame, config: HyperstyleEvaluationConfig) -> pd.DataFrame:
    """ Run hyperstyle tool on solutions. """
    df_solutions = evaluate_by_solution(df_solutions, config, parse_hyperstyle_result,
                                        working_directory=config.working_directory)
    return df_solutions


def main():
    parser = argparse.ArgumentParser()
    configure_arguments(parser)

    start = time.time()
    args = parser.parse_args()

    df_solutions = read_df(args.solutions_file_path)
    config = HyperstyleEvaluationConfig(tool_path=args.tool_path,
                                        allow_duplicates=args.allow_duplicates,
                                        with_all_categories=args.with_all_categories,
                                        tmp_path=args.tmp_directory,
                                        disable=args.disable,
                                        working_directory=args.working_directory,
                                        venv=args.venv)

    logger.info('Start processing:')
    results = evaluate_hyperstyle(df_solutions, config)
    if args.output_path is None:
        output_path = get_output_path(args.solutions_file_path, HYPERSTYLE_OUTPUT_SUFFIX)
    else:
        output_path = args.output_path / get_output_filename(args.solutions_file_path, HYPERSTYLE_OUTPUT_SUFFIX)
    write_df(results, output_path)
    end = time.time()
    logger.info(f'Total processing time: {end - start}')


if __name__ == '__main__':
    sys.exit(main())
