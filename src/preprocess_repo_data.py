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


@hydra.main(config_path="conf", config_name="config", version_base=None)
def main(cfg: ReposConfig):

    repo_processor = RowRepoDataProcessor()


if __name__ == "__main__":
    main()
