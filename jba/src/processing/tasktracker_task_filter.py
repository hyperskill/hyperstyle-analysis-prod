import argparse
from pathlib import Path
import pandas as pd
from datetime import datetime
from pytz import UTC

from core.src.utils.df_utils import read_df, write_df

PACKAGE_PATTERN = r'package ([\w\.]+)'
FRAGMENT_COLUMN = 'fragment'
TASK_COLUMN = 'task'
DATE_COLUMN = 'date'
DATE_FORMAT = '%d.%m.%Y'


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        'document_path',
        type=lambda value: Path(value).absolute(),
        help='Path to documentdata.csv.',
    )

    parser.add_argument(
        'destination_path',
        type=lambda value: Path(value).absolute(),
        help='Path of the file to save filtered data',
    )

    parser.add_argument(
        'start_date',
        type=str,
        help='Start of the research in the DD.MM.YYYY format',
    )


def filter_data(document_path: Path, destination_path: Path, date: str) -> None:
    data = read_df(document_path)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    filtered_data = data[data[DATE_COLUMN] > datetime.strptime(date, DATE_FORMAT).replace(tzinfo=UTC)].copy()
    filtered_data[TASK_COLUMN] = filtered_data[FRAGMENT_COLUMN].str.extract(PACKAGE_PATTERN)
    write_df(filtered_data, destination_path)


def main():
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    args = parser.parse_args()
    filter_data(args.document_path, args.destination_path, args.start_date)


if __name__ == '__main__':
    main()
