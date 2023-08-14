import ast
import pandas as pd

from typing import Optional, List

from core.src.model.column_name import StepColumns
from core.src.utils.quality.code_utils import split_code_to_lines


def parse_template_code_from_step(step: pd.Series, lang: Optional[str] = None, keep_ends: bool = False) -> List[str]:
    # Steps gathered from Database in format of str
    code_template = step.get(StepColumns.CODE_TEMPLATE.value)
    if not pd.isna(code_template):
        return parse_template_code_from_str(code_template, keep_ends=keep_ends)

    # Steps gathered from API in format of dict
    if StepColumns.CODE_TEMPLATES.value in step and lang is not None:
        return parse_template_from_dict(step[StepColumns.CODE_TEMPLATES.value], lang=lang, keep_ends=keep_ends)

    raise Exception(  # noqa: WPS454
        'Can not parse template code! Check the language is specified and dataset has corresponding columns!',
    )


def parse_template_code_from_str(template_str: str, keep_ends: bool = False) -> List[str]:
    return split_code_to_lines(template_str, keep_ends=keep_ends)


def parse_template_from_dict(template_dict: str, lang: Optional[str] = None, keep_ends: bool = False) -> List[str]:
    templates_code = ast.literal_eval(template_dict)
    return split_code_to_lines(templates_code[lang], keep_ends=keep_ends)


# TODO: support multi-line comments
def is_comment(code_line) -> bool:
    return code_line.lstrip().startswith("#") or code_line.lstrip().startswith("//")

