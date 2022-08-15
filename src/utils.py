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


def list_repo_files(repo_dir: Path) -> Dict[str, Path]:
    """Returns paths list of feature file in a repository directory.

    Args:
        repo_dir (Path): Path to the repository directory

    Returns:
        Dict[str, Path]: List of feature file path of repository.
    """
    # if not get_repo_path(repo_dir):
    #     raise NotFoundError(f'Path Does not Exist: "{repo_dir}" not found.')
    # elif len(list(repo_dir.iterdir())) == 0:
    #     raise FileDirEmptyError(f"Empty File or Directory:{repo_dir}")
    repo_path = get_repo_path(repo_dir)
    if repo_path is None:
        print("Something went wrong")
    repo_lsit = {r_file.stem: r_file for r_file in repo_path.glob("*.csv")}
    return repo_lsit


def get_feat_file(feature_name: str, repo_dir: Path) -> Path:
    """Gets a data of given repository's feature file(e.g commits).

    Args:
        feature_name (str): Repositiy Feature name.
        repo_dir (Path): Path of the repository.

    Returns:
        Path: Path of the feature file.
    """
    repo_path = get_repo_path(repo_dir)
    if repo_path is None:
        print("Something went wrong")
    repo_files = list_repo_files(repo_dir)
    return repo_files[feature_name]


def get_save_path(
    feature_name: str,
    repos_dir: Path,
    save_dir: Path,
    parent: bool,
) -> Path:
    """Creates a path to save the processed File or Directory.

    Args:
        feature_name (str): Repositiy Feature name.
        repos_dir (Path): Path of Directory of the repositories.
        save_dir (Path): Path to save the processed File or Directory.
        parent (bool): Treu if the you want to keep the original parent directory name.
                        False if you want just to save unter the current directory.

    Returns:
        Path: Path to save the processed File or Directory.
    """

    if not save_dir.exists():
        save_dir.mkdir(exist_ok=True)
    repo_name = repos_dir.name
    parent_dir = list(repos_dir.parents)[0].name

    if not parent:
        saving_path = (save_dir / f"{repo_name}_{feature_name}").with_suffix(".csv")
        # print(repo_name, repo_lang_dir)
    else:
        saving_path = save_dir / parent_dir / repo_name
        saving_path.mkdir(parents=True, exist_ok=True)
        saving_path = (saving_path / f"{feature_name}").with_suffix(".csv")

    if not saving_path.exists():
        saving_path.touch()
        return saving_path
    return saving_path
