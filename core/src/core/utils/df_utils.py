from pathlib import Path
from typing import Iterable, Union, Optional

import pandas as pd

from core.utils.file.extension_utils import get_restricted_extension, AnalysisExtension


def filter_df_by_iterable_value(df: pd.DataFrame, column: str, value: Iterable) -> pd.DataFrame:
    return df.loc[df[column].isin(value)]


def read_df(path: Union[str, Path]) -> Optional[pd.DataFrame]:
    """ Read dataframe from given .csv. """

    ext = get_restricted_extension(path, [AnalysisExtension.CSV])
    if ext == AnalysisExtension.CSV:
        return pd.read_csv(path)

    raise NotImplementedError(f'Can not read df with extension {ext.value}')


def write_or_pint_df(df: pd.DataFrame, path: Optional[Union[str, Path]]):
    if path is None:
        print(df)
    else:
        write_df(df, path)


def write_df(df: pd.DataFrame, path: Union[str, Path]):
    """ Write dataframe to given .csv. """

    ext = get_restricted_extension(path, [AnalysisExtension.CSV])
    if ext == AnalysisExtension.CSV:
        df.to_csv(path, index=False)
    else:
        raise NotImplementedError(f'Can not write df with extension {ext.value}')


def equal_df(expected_df: pd.DataFrame, actual_df: pd.DataFrame) -> bool:
    return (expected_df.empty and actual_df.empty) or expected_df.reset_index(drop=True).equals(
        actual_df.reset_index(drop=True))


def merge_dfs(df_left: pd.DataFrame, df_right: pd.DataFrame, left_on: str, right_on: str, how='inner') -> pd.DataFrame:
    """ Merge two given dataframes on `left_on` = `right_on`. Duplicated columns are removed. """

    df_merged = pd.merge(df_left, df_right, how=how, left_on=left_on, right_on=right_on, suffixes=('', '_extra'))
    df_merged.drop(df_merged.filter(regex='_extra$').columns.tolist(), axis=1, inplace=True)
    return df_merged
