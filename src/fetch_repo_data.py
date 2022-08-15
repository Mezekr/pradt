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
            repo (Union[str, List[str]]): Accepts either a repository name or
            a list of repository names.
            save_path (Path): Directory path object to save the repository
            related file.
        """
        self.repo_path = repo
        self.save_path = save_path

    def get_github_user(self) -> Optional[Github]:
        """Authorize GitHub users through tokens (if provided) and return User.

        Returns:
            Optional[Github]: GitHub Authorized User.
        """
        TOKEN = dotenv_values(".env")["TOKEN"]
        if not TOKEN or TOKEN.isspace():

            print(
                "Tip: A GitHub access token has not been provided. Get the  \
                access token from GitHub to get more requests from users to the \
                the server (i.e. 5000 requests per hour instead of 60)."
            )
        try:
            git_user = Github(TOKEN, retry=50, timeout=10, per_page=100)
            return git_user
        except BadCredentialsException as e:
            print(e.status)
            print("Limit exceeded")

    def check_API_ratelimit(self, github_user: Github, min_limit: int) -> None:
        """checks the GitHub API rate limit and the remaining rate.
        Args:
            github_user (Github): GitHub Authorized User.
            min_limit (int): Minimum limit to be checked against
                            before the rate limit is reached.
        """
        try:
            requests_remaning, requests_limit = github_user.rate_limiting
            if (requests_limit == 5000) & (requests_remaning < min_limit):
                print(requests_remaning, requests_limit)
                reset_timestamp = github_user.rate_limiting_resettime
                seconds_until_reset = reset_timestamp - time.time()
                minutes = math.ceil(seconds_until_reset / 60)
                print(f"Waiting for {minutes} minutes to refresh request limit...")
                for i in range(minutes):
                    print(
                        "%s[%s%s] %i/%i"
                        % ("Sleeping ", "#" * i, "." * (minutes - i), i, minutes),
                        end="",
                        flush=True,
                    )
                time.sleep(60)
                print(end="\r")
        except GithubException as e:
            print(e)

    def create_repos_dir(self) -> Path:
        """creates a directory for the resulting repository files.

        Returns:
            Path: Directory path to the resulting repository files.
        """
        repos_dir = self.save_path
        if not repos_dir.is_dir():
            Path.mkdir(repos_dir, exist_ok=True)
            return repos_dir
        return repos_dir

    def create_repo_dir(self, repo_name: str, show_msg: bool = False) -> Path:
        """creates a sub-directory for the resulting repository-related data files.

        Args:
            repo_name (str): Repository's full name
            show_msg (bool, optional): To show the message if the directory already exists.
                                        Defaults to False.

        Returns:
            Path: Path of repository sub-directory to be created.
        """

        dataset_dir = self.create_repos_dir()
        repo_name = repo_name.split("/")[-1]
        repo_path = Path(dataset_dir, repo_name)

        if not repo_path.exists():
            Path.mkdir(repo_path, exist_ok=True)
            print(f"{repo_name}: New dir is created ")
            logging.info(f"{repo_name}: New dir is created ")
        else:
            if show_msg:
                print(f"{repo_name}: Dir exist already ")
                logging.info(f"{repo_name}: Dir exist already ")
        return repo_path

    def check_file(self, repo_name: str, repo_file: str = None) -> Tuple[bool, Path]:
        """Checks whether the file or directory of a repository already exists

        Args:
            repo_name (str): Repository's full name
            repo_file (str, optional): repository data file(e.g commit, fork). Defaults to None.

        Returns:
            Tuple[bool, Path]: Returns True or False and the file path if the file exit or not
        """
        repo_dir = self.create_repo_dir(repo_name)
        file_to_save = Path(repo_dir, f"{repo_file}").with_suffix(".csv")
        if file_to_save.exists():
            return (True, file_to_save)
        return (False, file_to_save)


@hydra.main(config_path="conf", config_name="config", version_base=None)
def main(cfg: ReposConfig):
    pass


if __name__ == "__main__":
    main()
