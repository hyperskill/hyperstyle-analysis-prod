import csv
import logging
import os
from dataclasses import asdict
from typing import List, TypeVar

from core.src.model.api.platform_objects import Object


class CsvWriter:

    def __init__(self, result_dir: str, csv_file: str, field_names: List[str]):
        os.makedirs(result_dir, exist_ok=True)
        self.csv_path = os.path.join(result_dir, csv_file)
        self.fieldnames = field_names

        with open(self.csv_path, 'w+', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=field_names)
            writer.writeheader()

    def write_csv(self, data: dict):
        with open(self.csv_path, 'a+', newline='', encoding='utf8') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writerow({k: data[k] for k in self.fieldnames})


T = TypeVar('T', bound=Object)


def save_objects_to_csv(output_path: str, objects: List[T], obj_class: str):
    if len(objects) == 0:
        return

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    logging.info(f'Writing {len(objects)} of type {type(objects[0])} to csv: {output_path}/{obj_class}s.csv')
    csv_writer = CsvWriter(output_path, f'{obj_class}s.csv', list(type(objects[0]).__annotations__.keys()))
    for obj in objects:
        csv_writer.write_csv(asdict(obj))
