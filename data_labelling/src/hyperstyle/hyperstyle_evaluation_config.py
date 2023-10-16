import json
import logging.config
import platform
import sys
from pathlib import Path
from typing import List, Optional, Union, Dict

from hyperstyle.src.python.review.application_config import LanguageVersion

from data_labelling.src.utils.evaluation_config import EvaluationConfig, OUTPUT_FILE_PATH

logger = logging.getLogger(__name__)

HYPERSTYLE_TOOL_PATH = 'review/hyperstyle/src/python/review/run_tool.py'


class HyperstyleEvaluationConfig(EvaluationConfig):
    def __init__(
        self,
        tool_path: str,
        allow_duplicates: bool,
        with_all_categories: bool,
        new_format: bool,
        tmp_path: Path,
        n_cpu: Optional[int] = None,
        disable: Optional[str] = None,
        working_directory: Optional[str] = None,
        venv: Optional[str | Path] = None,
        ij_config: Optional[Dict] = None,
    ):
        """
        `tool_path` - path to hyperstyle tool running script (custom or HYPERSTYLE_TOOL_PATH)
        `tmp_path` - path where to place evaluation temporary files
        Number of hyperstyle tool running script parameters (`allow_duplicates`, `with_all_categories` etc.)
        """

        super().__init__(tmp_path=tmp_path / 'hyperstyle',
                         result_path=OUTPUT_FILE_PATH,
                         with_template=False)

        self.tool_path: str = tool_path

        self.allow_duplicates: bool = allow_duplicates
        self.with_all_categories: bool = with_all_categories
        self.new_format: bool = new_format
        self.n_cpu: int = n_cpu
        self.disable: Optional[str] = disable
        self.ij_config: Optional[Dict[str, Dict[str, str]]] = ij_config
        self.working_directory: Optional[str] = working_directory
        self.venv: Optional[str | Path] = venv

    def build_command(self,
                      input_path: Union[str, Path],
                      output_path: Union[str, Path],
                      language_version: LanguageVersion,
                      submission_path: Optional[Path]) -> List[str]:

        # TODO: move to a variable
        if self.venv is not None:
            python = f'{self.venv}/bin/python'
        else:
            python = sys.executable
        python_command = [python, f'{self.tool_path}']

        if self.allow_duplicates:
            python_command += ['--allow-duplicates']

        if self.with_all_categories:
            python_command += ['--with-all-categories']

        if self.new_format:
            python_command += ['--new-format']

        if self.n_cpu:
            python_command += ['--n-cpu', str(self.n_cpu)]

        if language_version.is_java():
            python_command += ['--language_version', language_version.value]

        if self.disable:
            python_command += ['--disable', self.disable]

        if self.ij_config:
            python_command += ['--ij-config', json.dumps(self.ij_config)]

        if platform.system() == 'Darwin':
            bash_prefix = None
        else:
            bash_prefix = ['/bin/bash', '-c']

        if submission_path is not None:
            path_to_inspect = submission_path
        else:
            path_to_inspect = input_path

        python_command += [str(path_to_inspect)]
        command = []
        if bash_prefix is not None:
            command += bash_prefix
        command += python_command

        return command
