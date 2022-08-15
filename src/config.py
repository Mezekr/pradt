from dataclasses import dataclass


@dataclass
class Paths:
    log: str
    raw_data: str
    processed_data: str
    final_data: str


@dataclass
class Files:
    final: str


@dataclass
class Params:
    epoch: int
    lr: float
    batch_size: int


@dataclass
class RepoFeatures:
    repo_data: str
    commits: str
    issues_pulls: str
    forks: str
    stargazer: str
    contributors: str
    watchers: str


@dataclass
class RepoToFetch:
    repos_dir: str
    repo_data: str


@dataclass
class ReposConfig:
    paths: Paths
    files: Files
    params: Params
    features: RepoFeatures
    repos: RepoToFetch
