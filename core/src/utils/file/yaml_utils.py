from pathlib import Path
from typing import Any, Union, Dict

import yaml


def parse_yaml(path: Union[Path, str]) -> Any:
    with open(path) as file:
        return yaml.safe_load(file)


def read_yaml_field_content(yaml_file: Path, field_name: str, default: Any = None) -> Any:
    if not yaml_file.exists():
        raise ValueError(f'{field_name} does not exist.')

    parsed_yaml_file = parse_yaml(yaml_file)
    if parsed_yaml_file is None:
        raise ValueError(f'`{yaml_file} is empty.')

    return parsed_yaml_file.get(field_name, default)


def save_as_yaml(yaml_content: Dict, path: Path):
    with open(path, 'w') as file:
        yaml.dump(yaml_content, file)
