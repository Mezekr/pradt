from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import hydra
import matplotlib.pyplot as plt
import pandas as pd
from hydra.core.config_store import ConfigStore

import utils
from config import ReposConfig

cs = ConfigStore.instance()
cs.store(name="repo_config", node=ReposConfig)


class NotFoundError(Exception):
    """Exception raised when there is no File"""

    pass


class FileDirEmptyError(Exception):
    """Exception raised when there File or Directory is Empty"""

    pass


class RowRepoDataProcessor:
    """class to prepocess the raw repository data"""

    def __init__(self):
        """Row repository data processor"""
        pass

    def __str__(self):
        return "Row repository data processor "

    def __repr__(self):
        return "Row repository data processor "

    def process_commits(
        self, feature_name: str, repo_dir: str, save_path: str
    ) -> Union[pd.DataFrame, pd.Series]:
        """Creates(Returns) a DataFrame of the Commits time series Data.

        Args:
            feature_name (str): Feature(commit) of repository to be processed.
            repo_dir (str): Directory path of the repository to be processed.
            save_path (str):  Directory path to save Commit time series data.

        Returns:
            Union[pd.DataFrame, None]: Returns Dataframe of the Commits time series data.
        """
        # save_to: Path = Path(save_path)

        # if not (repo_path.exists() and save_to.exists()):
        #     raise NotFoundError(
        #         f'Path Does not Exist: "{repo_path} or {save_to}" not found.'
        #     )
        repo_path, save_to = utils.set_path(repo_dir, save_path)
        raw_file = utils.get_feat_file(feature_name, repo_path)

        feat_df = pd.read_csv(
            raw_file, parse_dates=["commit_date"], index_col="commit_date"
        )
        feat_resample = feat_df.commit_count.resample("D").count()

        processed_file_path = utils.get_save_path(
            feature_name, repo_path, save_to, True
        )
        feat_resample.to_csv(processed_file_path)
        print("Commits processed successfully")
        return feat_resample

    def process_forks(
        self, feature_name: str, repo_dir: str, save_path: str
    ) -> Union[pd.DataFrame, pd.Series]:
        """Creates(Returns) a DataFrame of the Forks time series Data.

        Args:
            feature_name (str): Feature(fork) of repository to be processed.
            repo_dir (str): Directory path of the repository to be processed.
            save_path (str):  Directory path to save Forks time series data.

        Returns:
            Union[pd.DataFrame, None]: Returns Dataframe of the Forks time series data.
        """

        # save_to: Path = Path(save_path)
        # if not (repo_path.exists() and save_to.exists()):
        #     raise NotFoundError(
        #         f'Path Does not Exist: "{repo_path} or {save_to}" not found.'
        #     )
        repo_path, save_to = utils.set_path(repo_dir, save_path)
        raw_file = utils.get_feat_file(feature_name, repo_path)
        print(raw_file)

        feat_df = pd.read_csv(raw_file, parse_dates=["forked_at"])
        feat_df = feat_df.groupby(pd.Grouper(key="forked_at", freq="D"))
        feat_resample = feat_df["forked_at"].count().to_frame(name="forks_count")

        processed_file_path = utils.get_save_path(
            feature_name, repo_path, save_to, True
        )
        feat_resample.to_csv(processed_file_path)
        print("Forks processed successfully")
        return feat_resample

    def process_issue_pullrequest(
        self, feature_name: str, repo_dir: str, save_path: str
    ) -> Union[pd.DataFrame, pd.Series]:
        """Returns or creates a DataFrame of the issue pull request time series Data.

        Args:
            feature_name (str): Feature(isse_pullrequest) of repository to be processed.
            repo_dir (str): Directory path of the repository to be processed.
            save_path (str):  Directory path to save issues and pull requests time series data.

        Returns:
            Union[pd.DataFrame, None]: Returns Dataframe of the Stars time series data.
        """

        # save_to: Path = Path(save_path)
        # if not (repo_path.exists() and save_to.exists()):
        #     raise NotFoundError(
        #         f'Path Does not Exist: "{repo_path} or {save_to}" not found.'
        #     )
        repo_path, save_to = utils.set_path(repo_dir, save_path)
        raw_file = utils.get_feat_file("issues_pulls", repo_path)

        feat_resample = pd.read_csv(
            raw_file,
            parse_dates=[
                "pr_iss_opened_at",
                "pr_iss_updated_at",
                "pr_iss_closed_at",
            ],
            infer_datetime_format=True,
        )

        pris_open_df = feat_resample.groupby(
            pd.Grouper(key="pr_iss_opened_at", freq="D")
        )
        pris_grp_open_df = (
            pris_open_df["pr_iss_opened_at"].count().to_frame(name="pr_iss_Open_count")
        )

        pris_lt_update = feat_resample.groupby(
            pd.Grouper(key="pr_iss_updated_at", freq="D")
        )
        pris_grp_ltpdate_df = (
            pris_lt_update["pr_iss_updated_at"]
            .count()
            .to_frame(name="pr_iss_updated_count")
        )
        pris_closed_df = feat_resample.groupby(
            pd.Grouper(key="pr_iss_closed_at", freq="D")
        )
        pris_grp_closed_df = (
            pris_closed_df["pr_iss_closed_at"]
            .count()
            .to_frame(name="pr_is_closed_count")
        )

        ps_merged_df = pd.merge(
            pris_grp_open_df,
            pris_grp_ltpdate_df,
            how="outer",
            left_index=True,
            right_index=True,
        )
        ps_merged_df = pd.merge(
            ps_merged_df,
            pris_grp_closed_df,
            how="outer",
            left_index=True,
            right_index=True,
        )
        processed_file_path = utils.get_save_path(
            feature_name, repo_path, save_to, True
        )
        ps_merged_df.to_csv(processed_file_path)

        return ps_merged_df

    def process_stargazer(
        self, feature_name: str, repo_dir: str, save_path: str
    ) -> Union[pd.DataFrame, pd.Series]:
        """Creates a stars time series data.

        Args:
            feature_name (str): Feature(stars) of repository to be processed.
            repo_dir (str): Directory path of the repository to be processed.
            save_path (str):  Directory path to save Stars time series data.

        Returns:
            Optional[pd.DataFrame]: Returns Dataframe of the Stars time series data.
        """
        # save_to: Path = Path(save_path)
        # if not (repo_path.exists() and save_to.exists()):
        #     raise NotFoundError(
        #         f'Path Does not Exist: "{repo_path} or {save_to}" not found.'
        #     )
        repo_path, save_to = utils.set_path(repo_dir, save_path)
        raw_file = utils.get_feat_file(feature_name, repo_path)

        feat_df = pd.read_csv(raw_file, parse_dates=["starred_at"])
        feat_df = feat_df.groupby(pd.Grouper(key="starred_at", freq="D"))
        feat_resample = feat_df["starred_at"].count().to_frame(name="Stars_count")

        processed_file_path = utils.get_save_path(
            feature_name, repo_path, save_to, True
        )
        feat_resample.to_csv(processed_file_path)

        return feat_resample

    def agg_repo_feat(self, row_data_dir: str, save_path: str) -> None:
        """Aggregates individual repository feature data.
        Args:
            repos_dir (str): Path of Directory of the repositories to be processed.
            save_path (str): Path of Directory to save the  processed repositories.

        """
        # save_to: Path = Path(save_path)
        # row_data_path: Path = Path(row_data_dir)
        # if not (row_data_path.exists() and save_to.exists()):
        #     raise NotFoundError(
        #         f'Path Does not Exist: "{row_data_path} or {save_to}" not found.'
        #     )
        row_data_path, save_to = utils.set_path(row_data_dir, save_path)
        dir_list = utils.list_repos_dirs(row_data_path)
        print(f"Aggrigating {len(dir_list)} repositories feature....")
        for repo_path in dir_list:
            print(repo_path)

            commits = self.process_commits("commits", str(repo_path), save_path)
            forks = self.process_forks("forks", str(repo_path), save_path)
            stars = self.process_stargazer("stargazer", str(repo_path), save_path)
            pris = self.process_issue_pullrequest(
                "issues_pulls", str(repo_path), save_path
            )

            merged_df = pd.merge(
                commits, forks, how="outer", left_index=True, right_index=True
            )
            merged_df = pd.merge(
                merged_df, stars, how="outer", left_index=True, right_index=True
            )
            merged_df = pd.merge(
                merged_df, pris, how="outer", left_index=True, right_index=True
            )
            merged_NaN_df = merged_df.fillna(0)
            processed_file_path = utils.get_save_path(
                "all_feature", repo_path, save_to, True
            )
            merged_NaN_df.to_csv(processed_file_path, index_label="date")
        print("Repository features has been merged successfully")

    def agg_repos_generic_data(self, repos_dir: str, save_path: str) -> Optional[Path]:
        """Aggregates all repositoreies generic data in to one File.

        Args:
            repos_dir (str): Path of Directory of the repositories to be processed.
            save_path (str): Path of Directory to save the  processed repositories.

        Returns:
            Optional[Path]: Path, where the generic data is saved.
        """
        repos_path, save_to = utils.set_path(repos_dir, save_path)

        concat_df = pd.DataFrame()
        for repo_path in utils.list_repos_dirs(repos_path):
            raw_file = utils.get_feat_file("repo_data", repo_path)
            temp_df = pd.read_csv(raw_file)
            concat_df = pd.concat([concat_df, temp_df], ignore_index=True)
        concat_df.drop_duplicates(subset=["repo_name", "language"], inplace=True)
        saving_path = utils.get_save_path(
            "generic_repos_data", repos_path, save_to, False
        )
        concat_df.to_csv(saving_path, index=False)

        return saving_path

    def gen_repos_age(self, repos_dir: str, save_path: str) -> None:
        """Genrates repository age in days.

        Args:
            repos_dir (str): Path of Directory of the repositories to be processed.
            save_path (str): Path of Directory to save the  processed repositories.
        """

        repos_path, save_to = utils.set_path(repos_dir, save_path)
        generic_data = self.agg_repos_generic_data(repos_dir, save_path)
        # print(generic_data)
        days_cols = ["created_at", "pushed_at", "last_update_at"]
        age_df = pd.read_csv(
            generic_data, parse_dates=days_cols, infer_datetime_format=True
        )
        age_df["age_in_weeks"] = age_df.apply(
            lambda row: ((row.last_update_at - row.created_at).days) // 7, axis=1
        )
        saving_path = utils.get_save_path(
            "generic_repos_data", repos_path, save_to, False
        )
        age_df.to_csv(saving_path, index=False)

        return age_df

    def get_all_feat_data(self, repos_dir: str, save_path: str) -> None:
        """Gets the file contains all features of a repository.

        Args:
            repos_dir (str): Path of Directory of the repositories to be processed.
            save_path (str): Path of Directory to save the  processed repositories.
        """

        repo_dir, save_to = utils.set_path(repos_dir, save_path)
        dir_list = utils.list_repos_dirs(repo_dir)
        print(f"Aggrigating {len(dir_list)} repositories feature....")
        for repo_path in utils.list_repos_dirs(repo_dir):

            parent = list(repo_path.parents)[0].name
            ff = utils.get_feat_file("all_feature", repo_path)
            # print(ff)
            feat_df = pd.read_csv(ff)

            ff_save = utils.get_save_path(
                f"all_feature_{parent}", repo_path, save_to, False
            )
            feat_df.to_csv(ff_save, index=False)


@hydra.main(config_path="conf", config_name="config", version_base=None)
def main(cfg: ReposConfig):

    repo_processor = RowRepoDataProcessor()


if __name__ == "__main__":
    main()
