import json
import zipfile
from pathlib import Path
from typing import List, Tuple, Dict, Any

import pandas as pd

from core.src.model.column_name import SubmissionColumns
from core.src.utils.file.file_utils import create_directory
from core.src.utils.subprocess_runner import run_in_subprocess
from jba.src.jplag.jplag_config import JPlagConfiguration
from jba.src.models.edu_columns import EduColumnName

RESULTS_FOLDER_NAME = 'results'
RESULT_ARCHIVE_NAME = 'result'
SUBMISSIONS_FOLDER_NAME = 'submissions'


class JPlagRunner:
    @staticmethod
    def build_arguments(
        task_id: int,
        output_dir: Path,
        jar_dir: Path,
        config: JPlagConfiguration,
    ) -> Tuple[Dict[str, Any], Dict[str, bool]]:
        submissions_path = output_dir / SUBMISSIONS_FOLDER_NAME / str(task_id)

        result_dir = output_dir / RESULTS_FOLDER_NAME / str(task_id) / config.to_file_path() / RESULT_ARCHIVE_NAME

        named_args = {
            'jarDir': jar_dir,
            'rootDir': submissions_path,
            '-l': 'kotlin',
            '-n': -1,
            '-r': result_dir,
            '--cluster-alg': config.algorithm.value,
            '--cluster-metric': config.metric.value,
            '--cluster-spectral-bandwidth': config.bandwidth,
            '--cluster-spectral-noise': config.noise,
            '--cluster-spectral-min-runs': config.min_runs,
            '--cluster-spectral-max-runs': config.max_runs,
            '--cluster-spectral-kmeans-interations': config.k_means_iterations,
            '--cluster-agglomerative-threshold': config.threshold,
            '--cluster-agglomerative-inter-cluster-similarity': config.inter_cluster_similarity.value,
        }

        flag_args = {
            config.preprocessing.to_cli_flag(): True,
        }

        return named_args, flag_args

    @staticmethod
    def configure_cmd(named_args: Dict[str, Any], flag_args: Dict[str, bool]) -> List[str]:
        cmd = 'java -jar'

        for arg_name, arg_value in named_args.items():
            if arg_name.startswith('-'):
                cmd = f'{cmd} {arg_name} {arg_value}'
            else:
                cmd = f'{cmd} {arg_value}'

        for arg_name, arg_value in flag_args.items():
            if arg_value:
                cmd = f'{cmd} {arg_name}'

        return cmd.split()

    def run(self, task_id: int, output_dir: Path, jar_dir: Path, config: JPlagConfiguration) -> str:
        create_directory(output_dir / RESULTS_FOLDER_NAME / str(task_id) / config.to_file_path())

        named_args, flag_args = self.build_arguments(task_id, output_dir, jar_dir, config)
        cmd = self.configure_cmd(named_args, flag_args)
        stdout, stderr = run_in_subprocess(cmd)

        return stderr


def create_submission_files(submissions: pd.DataFrame, output_dir: Path) -> List[int]:
    """
    Create code submissions files from .csv file in JPlag form

    :param submissions_csv_file_path: path to .csv file storing code submissions
    :param output_dir: directory storing all output files

    :return: list of all task ids
    """
    tasks = submissions[EduColumnName.TASK_ID.value].unique()

    submissions_dir = output_dir / SUBMISSIONS_FOLDER_NAME
    for task in tasks:
        task_dir = submissions_dir / str(task)
        create_directory(task_dir)
        task_df = submissions[submissions[EduColumnName.TASK_ID.value] == task]
        for _, row in task_df.iterrows():
            sub_id = row[SubmissionColumns.ID.value]
            with open(task_dir / f'{sub_id}.kt', 'w') as f:
                f.write(row[SubmissionColumns.CODE.value])

    return tasks


def get_clusters(task_id: int, config: JPlagConfiguration, output_dir: Path) -> List[List[int]]:
    """
    Parse clusters from JPlag results

    :param task_id: task id
    :param threshold: clustering threshold
    :param output_dir: directory storing all output files (including JPlag result)
    :return: list of all found clusters (as lists of submissions ids)
    """

    def cluster_members_to_submission_ids(members: List[str]) -> List[int]:
        return [int(Path(sub_file).stem) for sub_file in members]

    result_archive_path = (
        output_dir / RESULTS_FOLDER_NAME / str(task_id) / config.to_file_path() / f'{RESULT_ARCHIVE_NAME}.zip'
    )

    with zipfile.ZipFile(result_archive_path) as z:
        with z.open('overview.json') as f:
            data = json.load(f)

    return [cluster_members_to_submission_ids(cl['members']) for cl in data['clusters']]
