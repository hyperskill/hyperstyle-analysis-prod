import argparse
import json
import logging
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
from hyperstyle.src.python.review.application_config import LanguageVersion
from hyperstyle.src.python.review.common.language import Language

from core.src.model.column_name import SubmissionColumns
from core.src.utils.df_utils import read_df, write_df
from core.src.utils.file.file_utils import get_output_path
from data_labelling.src.hyperstyle.evaluate import evaluate_hyperstyle
from data_labelling.src.hyperstyle.hyperstyle_evaluation_config import HyperstyleEvaluationConfig
from jba.src.models.edu_columns import EduColumnName

logger = logging.getLogger(__name__)


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        'submissions_path',
        type=lambda value: Path(value).absolute(),
        help='Path to .csv file with submissions.',
    )

    parser.add_argument(
        '--tool-path',
        type=lambda value: Path(value).absolute(),
        help='Path to the Hyperstyle entry point.',
        required=True,
    )

    parser.add_argument(
        '--language-version',
        choices=LanguageVersion.values(),
        help='Language version of code snippets.',
        required=True,
    )

    parser.add_argument(
        '--host',
        help='Code quality server address.',
        required=True,
    )

    parser.add_argument(
        '--port',
        type=int,
        help='Code quality server port.',
        required=True,
    )

    parser.add_argument(
        '--venv',
        type=lambda value: Path(value).absolute(),
        help='Path to venv to run the tool.',
    )

    parser.add_argument('--disable', help='List of inspectors to disable. Example: `pylint,flake8`.')

    parser.add_argument(
        '--debug',
        help='Run the script in debug mode.',
        action='store_true',
    )

    parser.add_argument(
        '--script-logs-path',
        type=lambda value: Path(value).absolute(),
        help='Path to a file where to save script logs.',
    )


def _convert_submissions(submissions: pd.DataFrame, language_version: LanguageVersion) -> pd.DataFrame:
    # Converting submissions to a dataframe that could be processed by the data_labelling module
    df_solutions = submissions[[EduColumnName.ID.value, EduColumnName.CODE_SNIPPETS.value]]
    df_solutions = df_solutions.dropna(subset=[EduColumnName.CODE_SNIPPETS.value])
    df_solutions[EduColumnName.CODE_SNIPPETS.value] = df_solutions[EduColumnName.CODE_SNIPPETS.value].apply(json.loads)
    # TODO: gather inspections from all snippets simultaneously instead of individually
    df_solutions = df_solutions.explode(EduColumnName.CODE_SNIPPETS.value)

    # WPS359 is disabled due to false positive.
    df_solutions[['file_path', SubmissionColumns.CODE.value]] = df_solutions[EduColumnName.CODE_SNIPPETS.value].apply(  # noqa: WPS359
        lambda code_snippet: pd.Series([code_snippet['name'], code_snippet['text']])
    )

    df_solutions[SubmissionColumns.ID.value] = df_solutions.apply(
        lambda row: f'{row[EduColumnName.ID.value]}-{row["file_path"].replace("/", "_")}',
        axis=1,
    )

    df_solutions[SubmissionColumns.LANG.value] = language_version.value
    df_solutions.reset_index(inplace=True)

    return df_solutions


def evaluate_submissions(
    submissions: pd.DataFrame,
    language_version: LanguageVersion,
    config: HyperstyleEvaluationConfig,
) -> pd.DataFrame:
    df_solutions = _convert_submissions(submissions, language_version)

    inspections = (
        # Gathering inspections
        evaluate_hyperstyle(df_solutions, config)
        # Grouping inspections from the same submission into a dictionary
        .groupby('index')
        .apply(
            lambda group: json.dumps(
                group[['file_path', SubmissionColumns.HYPERSTYLE_ISSUES.value]]
                .rename(columns={'file_path': 'name', SubmissionColumns.HYPERSTYLE_ISSUES.value: 'text'})
                .to_dict('records')
            )
        )
        .rename(EduColumnName.INSPECTIONS.value)
    )

    return pd.concat([submissions, inspections], axis=1)


# TODO: fix a bug when the server fails on some submissions
def main():
    parser = argparse.ArgumentParser()
    configure_parser(parser)
    args = parser.parse_args()

    logging.basicConfig(
        filename=args.script_logs_path,
        level=logging.DEBUG if args.debug else logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',  # noqa: WPS323 You must use % here to format logger.
        force=True,
    )

    submissions = read_df(args.submissions_path)

    with TemporaryDirectory() as tmpdir:
        config = HyperstyleEvaluationConfig(
            tool_path=args.tool_path,
            allow_duplicates=False,
            with_all_categories=True,
            new_format=False,
            tmp_path=Path(tmpdir),
            venv=args.venv,
            disable=args.disable,
            ij_config={
                Language.from_language_version(LanguageVersion(args.language_version)).value.lower(): {
                    'host': args.host,
                    'port': args.port,
                },
            },
        )

        submissions = evaluate_submissions(submissions, LanguageVersion(args.language_version), config)

    write_df(submissions, get_output_path(args.submissions_path, '-with_inspections'))


if __name__ == '__main__':
    main()
