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

    def get_repo_info(self, repo_name: str) -> None:
        """Retrieve general information about the repository and saves it in
            the respective csv file under the repository Folder.

        Args:
            repo_name (str): Repository's full name.
        """

        file_exist, file_to_save = self.check_file(repo_name, "repo_data")
        if file_exist:
            print(f"{repo_name} {file_to_save.stem} file already exists")
            logging.info(f"{repo_name} {file_to_save.stem} file already exists")
        else:

            df_repo = pd.DataFrame()
            gh_user = self.get_github_user()
            self.check_API_ratelimit(gh_user, 50)
            repo = gh_user.get_repo(repo_name)
            df_repo = df_repo.append(
                {
                    "repo_name": repo_name,
                    "discription": repo.description,
                    "language": repo.language,
                    "user_Name": repo.url.split("/")[-2],
                    "created_at": pd.to_datetime(repo.created_at),
                    "pushed_at": pd.to_datetime(repo.pushed_at),
                    "last_update_at": pd.to_datetime(repo.updated_at),
                    "stars": repo.stargazers_count,
                    "size": repo.size,
                    "repo_url": repo.url,
                    "repo_html_url": repo.html_url,
                    "branch_count": repo.get_branches().totalCount,
                    "milestone_count": repo.get_milestones(state="all").totalCount,
                    "pullrequest_count": repo.get_pulls(state="all").totalCount,
                    "release_count": repo.get_releases().totalCount,
                    "workflow_count": repo.get_workflows().totalCount,
                    "issues_count": repo.get_issues(state="all").totalCount,
                    "watchers_count": repo.watchers_count,
                    "subscribers_count": repo.subscribers_count,
                    "has_wiki": bool(repo.has_wiki),
                    "has_pages": bool(repo.has_pages),
                    "has_projects": bool(repo.has_projects),
                    "has_downloads": bool(repo.has_downloads),
                },
                ignore_index=True,
            )

            df_repo.to_csv(file_to_save, index=False)
            print(f"{repo_name}: Repository Data file is created")
            logging.info(f"{repo_name}: Repository Data file is created")

    def get_commits_his(self, repo_name:str)-None:
        """Retrieve repository commits history and saves it in a corresponding
         commits CSV file under the repository folder. 

        Args:
            repo_name (str): Repository's full name.
        """

        file_exist, file_to_save = self.check_file(repo_name, "commits")
        if file_exist:
            print(f"{repo_name} {file_to_save.stem} file already exists")
            logging.info(f"{repo_name} {file_to_save.stem} file already exists")
        else:
            df_repo = pd.DataFrame()
            gh_user = self.get_github_user()
            remaning = self.check_API_ratelimit(gh_user, 100)
            repo = gh_user.get_repo(repo_name)

            repo_commits = repo.get_commits()
            r_commit_count = len(list(repo_commits))

            for index, commit in enumerate(repo_commits):
                remaning = self.check_API_ratelimit(gh_user, 25)
                commit_date = commit.commit.committer.date
                print(index, remaning, repo_name, r_commit_count, commit, commit_date)
                df_repo = df_repo.append(
                    {
                        "repo_name": repo_name,
                        "commit_count": r_commit_count,
                        "commit_sha": commit,
                        "commit_date": commit_date,
                    },
                    ignore_index=True,
                )

            df_repo.to_csv(file_to_save, index=False)
            print(f"{repo_name}: commits file is created")
            logging.info(f"{repo_name}: commits file is created")

    def get_issues_and_pull_his(self, repo_name:str)-> None:
        """Retrieve repository pull requests andissues history and saves it in a corresponding
         issues_pulls CSV file under the repository folder. 

        Args:
            repo_name (str): Repository's full name.
        """
        file_exist, file_to_save = self.check_file(repo_name, "issues_pulls")
        if file_exist:
            print(f"{repo_name} {file_to_save.stem} file already exists")
            logging.info(f"{repo_name} {file_to_save.stem} file already exists")
        else:
            df_repo = pd.DataFrame()
            gh_user = self.get_github_user()

            repo = gh_user.get_repo(repo_name)

            r_all_issues = repo.get_issues(state="all")
            for index, repo_issue in enumerate(r_all_issues):
                self.check_API_ratelimit(gh_user, 50)
                if repo_issue.pull_request:
                    Issue_or_pull = "pull request"
                else:
                    Issue_or_pull = "Issue"
                df_repo = df_repo.append(
                    {
                        "repo_name": repo_name,
                        "issue_pull": Issue_or_pull,
                        "pr_iss_state": repo_issue.state,
                        "pr_iss_opened_at": repo_issue.created_at,
                        "pr_iss_updated_at": repo_issue.updated_at,
                        "pr_iss_closed_at": repo_issue.closed_at,
                    },
                    ignore_index=True,
                )
            df_repo.to_csv(file_to_save, index=False)
            print(f"{repo_name}: Issues and pull requests file is created")
            logging.info(f"{repo_name}: Issues and pull requests file is created")

    def get_forks_his(self, repo_name:str)-> None:
        """Retrieve repository forks history and saves it in a corresponding
            forks CSV file under the repository folder. 


        Args:
            repo_name (str): Repository's full name.
        """

        file_exist, file_to_save = self.check_file(repo_name, "forks")
        if file_exist:
            print(f"{repo_name} {file_to_save.stem} file already exists")
            logging.info(f"{repo_name} {file_to_save.stem} file already exists")
        else:
            df_repo = pd.DataFrame()
            gh_user = self.get_github_user()

            repo = gh_user.get_repo(repo_name)

            repo_fork = repo.get_forks()

            for index, fork in enumerate(repo_fork):
                self.check_API_ratelimit(gh_user, 25)
                df_repo = df_repo.append(
                    {
                        "repo_name": repo_name,
                        "fork_count": repo_fork.totalCount,
                        "forked_user": fork.full_name,
                        "forked_at": fork.created_at,
                    },
                    ignore_index=True,
                )

            df_repo.to_csv(file_to_save, index=False)
            print(f"{repo_name}: forks file is created")
            logging.info(f"{repo_name}: forks file is created")

    def get_watchers_his(self, repo_name: str)-> None:
        """Retrieve repository Watchers history and saves it in a corresponding
            watchers CSV file under the repository folder. 

        Args:
            repo_name (str): Repository's full name.
        """

        file_exist, file_to_save = self.check_file(repo_name, "watchers")
        if file_exist:
            print(f"{repo_name} {file_to_save.stem} file already exists")
            logging.info(f"{repo_name} {file_to_save.stem} file already exists")
        else:
            df_repo = pd.DataFrame()
            gh_user = self.get_github_user()

            repo = gh_user.get_repo(repo_name)

            repo_subscribers = repo.get_subscribers()
            for index, subscriber in enumerate(repo_subscribers):
                self.check_API_ratelimit(gh_user, 25)
                df_repo = df_repo.append(
                    {
                        "repo_name": repo_name,
                        "watchers_count": repo.watchers_count,
                        "subscribers_count": repo.subscribers_count,
                        "subscriber": subscriber,
                        "subscriber_username": subscriber.login,
                        "subscribed_at": subscriber.created_at,
                    },
                    ignore_index=True,
                )
            df_repo.to_csv(file_to_save, index=False)
            print(f"{repo_name} : watchers/subscriber file is created")
            logging.info(f"{repo_name} : watchers/subscriber file is created")
    
    def get_contributors_his(self, repo_name:str)-> None:
        """Retrieve repository Contributors history and saves it in a corresponding
            Contributors CSV file under the repository folder. 

        Args:
            repo_name (str): Repository's full name.
        """

        file_exist, file_to_save = self.check_file(repo_name, "Contributors")
        if file_exist:
            print(f"{repo_name} {file_to_save.stem} file already exists")
            logging.info(f"{repo_name} {file_to_save.stem} file already exists")
        else:
            df_repo = pd.DataFrame()
            gh_user = self.get_github_user()
            repo = gh_user.get_repo(repo_name)
            all_contributos = repo.get_contributors(True).totalCount
            author_contributos = repo.get_contributors()

            contributers_count = author_contributos.totalCount
            print(
                f"Github provides only data of the {contributers_count} / {all_contributos} Contributors"
            )
            logging.info(
                f"Github provides only data of the {contributers_count} / {all_contributos} Contributors"
            )

            for index, contributer in enumerate(author_contributos):
                self.check_API_ratelimit(gh_user, 25)
                df_repo = df_repo.append(
                    {
                        "repo_name": repo_name,
                        "contributors_count": contributers_count,
                        "contributor": contributer.login,
                        "contributed_date": contributer.created_at,
                    },
                    ignore_index=True,
                )

            df_repo.to_csv(file_to_save, index=False)
            print(f"{repo_name}:  Contributors file is created")
            logging.info(f"{repo_name}:  Contributors file is created")

    def get_stargazer_his(self, repo_name: str)-> None:
        """Retrieve repository stargazer history and saves it in a corresponding
            stargazer CSV file under the repository folder. 

        Args:
            repo_name (str): Repository's full name.
        """


        file_exist, file_to_save = self.check_file(repo_name, "stargazer")
        if file_exist:
            print(f"{repo_name} {file_to_save.stem} file already exists")
            logging.info(f"{repo_name} {file_to_save.stem} file already exists")
        else:
            df_repo = pd.DataFrame()
            gh_user = self.get_github_user()
            repo = gh_user.get_repo(repo_name)
            repo_stars = repo.get_stargazers_with_dates()
            num_stars_returned = 0
            for index, star in enumerate(repo_stars):
                self.check_API_ratelimit(gh_user, 25)
                num_stars_returned = index + 1
                df_repo = df_repo.append(
                    {
                        "repo_name": repo_name,
                        "starred_user": star.user,
                        "starred_at": star.starred_at,
                    },
                    ignore_index=True,
                )

            if num_stars_returned < repo.stargazers_count:
                print(f"Because stars are more than {num_stars_returned}")
                print(f"Only the first {num_stars_returned} are returned from Github")
                print("#" * 25)

            df_repo.to_csv(file_to_save, index=False)
            print(f"{repo_name}: stargazer file has been created")
            logging.info(f"{repo_name}: stargazer file is created")
    
    def get_repo_data(self, repo_name:str)-> None:
        """ Gets all repository data.

        Args:
            repo_name (str): Repository's full name.
        """
        self.get_github_user()
        self.create_repo_dir(repo_name, show_msg=True)
        self.get_repo_info(repo_name)
        self.get_commits_his(repo_name)
        self.get_forks_his(repo_name)
        self.get_issues_and_pull_his(repo_name)
        self.get_stargazer_his(repo_name)
        self.get_watchers_his(repo_name)
        self.get_contributors_his(repo_name)

        print(f"{repo_name}: Repository data is successfully extracted.")
        logging.info(f"{repo_name}: Repository data is successfully extracted.")

@hydra.main(config_path="conf", config_name="config", version_base=None)
def main(cfg: ReposConfig):
    pass


if __name__ == "__main__":
    main()
