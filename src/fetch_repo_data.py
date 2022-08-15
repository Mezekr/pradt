import logging
import math
import time
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import hydra
import pandas as pd
from dotenv import dotenv_values
from github import Github
from github.GithubException import BadCredentialsException, GithubException
from hydra.core.config_store import ConfigStore

import utils
from config import ReposConfig

cs = ConfigStore.instance()
cs.store(name="repo_config", node=ReposConfig)

warnings.filterwarnings("ignore")
logging.basicConfig(
    filename="repos_his.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s: %(message)s",
)


class RepoDataFetcher:
    """Class for retrieving repository-related data from GitHub."""

    def __init__(self, repo: Union[str, List[str]], save_path: Path) -> None:
        """Initialization of the RepoDataFetcher class.

        Args:
            repo (Union[str, List[str]]): Accepts either a repository name or a list of repository names.
            save_path (Path): Directory path object to save the repository related file.
        """
        self.repo_path = repo
        self.save_path = save_path


@hydra.main(config_path="conf", config_name="config", version_base=None)
def main(cfg: ReposConfig):
    pass


if __name__ == "__main__":
    main()
