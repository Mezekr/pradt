import sys
from pathlib import Path
from typing import Callable, Dict, Iterator, List, Optional, Set, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from preprocess_repo_data import FileDirEmptyError, NotFoundError


def get_repo_path(repos_dir: Union[Path, str]) -> Optional[Path]:
    """Returns a path to a given repository.

    Args:
        repos_dir (Union[Path, str]): Path to a repository

    Raises:
        NotFoundError: If the Directory is not availably
        FileDirEmptyError: If the Directory is empty.
    Returns:
        Optional[Path]: Pathlib Path object.
    """

    try:
        if not isinstance(repos_dir, Path):
            repos_path: Path = Path(repos_dir)
        repos_path: Path = repos_dir
        if not repos_path.exists():
            raise NotFoundError(
                f'Path does not Exist: "{repos_path}" File or Directory not found.'
            )
        if len(list(repos_path.iterdir())) == 0:
            raise FileDirEmptyError(f"Empty File or Directory:{repos_path}")
        return repos_path
    except (NotFoundError, FileDirEmptyError) as e:
        print(e)

        sys.exit(1)
