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


def list_repos_dirs(repos_dir: Path) -> List[Path]:
    """Returns a list paths all directory of a repository in a directory.

    Args:
        repos_dir (str): Path of Directory of the repositories.

    Raises:
        NotFoundError: If the Directory is not availably.

    Returns:
        List[Path]: Repositoties path list.
    """

    # repos_path: Path = Path(repos_dir)
    # if not get_repo_path(repos_path):
    #     raise NotFoundError(f'Path Does not Exist: "{repos_path}" not found.')
    # elif len(list(repos_path.iterdir())) == 0:
    #     raise FileDirEmptyError(f"Empty File or Directory:{repos_path}")
    repos_path = get_repo_path(repos_dir)
    if repos_path is None:
        print("Something went wrong")
    dirs_list = {dir.name: dir for dir in repos_path.iterdir() if dir.is_dir()}
    # print(dirs_list)
    repo_dir = []
    for dir_path in dirs_list.values():
        if dir_path.is_dir():
            subdir = [dir for dir in dir_path.iterdir() if dir.is_dir()]
            if len(subdir) == 0:
                repo_dir.append(dir_path)
            repo_dir.extend([dir for dir in dir_path.glob("*") if dir.is_dir()])

    return repo_dir
