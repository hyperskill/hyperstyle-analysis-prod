import logging
import subprocess
from pathlib import Path
from typing import List, Optional, Union, Tuple

logger = logging.getLogger(__name__)


def run_in_subprocess(
    command: List[str],
    working_directory: Optional[Union[str, Path]] = None,
    encoding: str = 'utf-8',
    subprocess_input: Optional[str] = None,
    timeout: Optional[float] = None,
) -> Tuple[str, str]:
    process = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=working_directory,
        encoding=encoding,
        input=subprocess_input,
        timeout=timeout,
    )

    stdout = process.stdout
    stderr = process.stderr

    if stdout:
        logger.debug(f'{command[0]}\'s stdout:\n{stdout}')
    if stderr:
        logger.debug(f'An error occur during a subprocess call: {stderr}')

    return stdout, stderr
