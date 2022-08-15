from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import hydra
import matplotlib.pyplot as plt
import pandas as pd
import utils
from hydra.core.config_store import ConfigStore

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


@hydra.main(config_path="conf", config_name="config", version_base=None)
def main(cfg: ReposConfig):

    repo_processor = RowRepoDataProcessor()


if __name__ == "__main__":
    main()
