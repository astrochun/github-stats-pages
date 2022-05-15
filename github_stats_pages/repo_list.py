import json
from typing import Tuple, List, Dict

import pandas as pd
import requests

from .logger import app_log as log

SHORTEN_COLUMNS = [
    "id",
    "name",
    "html_url",
    "description",
    "language",
    "fork",
    "archived",
    "stargazers_count",
    "watchers_count",
    "has_issues",
    "has_downloads",
    "has_wiki",
    "has_pages",
    "forks_count",
    "disabled",
    "open_issues_count",
    "license",
    "forks",
    "open_issues",
    "watchers",
    "default_branch",
]


def get_repo_list(user: str) -> Tuple[list, pd.DataFrame]:
    """
    Get list of public repository for a give user

    :param user: GitHub user or organization handle (e.g., "numpy")
    :return repository_list: List of public repositories and additional info
    :return repository_df: DataFrame containing public repositories
    """

    log.info("[yellow]Retrieving repository list")

    endpoint = f"https://api.github.com/users/{user}/repos"
    params = {"per_page": 100}
    response = requests.get(endpoint, params=params)
    repository_list: List[Dict] = json.loads(response.content)

    repository_df = pd.DataFrame.from_dict(repository_list)

    log.info("[dark_green]Repository list retrieved!")
    return repository_list, repository_df


def construct_csv(repository_df: pd.DataFrame, csv_outfile: str):
    """
    Write CSV file with repository information

    :param repository_df: DataFrame containing results (see get_repo_list)
    :type repository_df: pandas.core.frame.DataFrame

    :param csv_outfile: Filename for output file
    :type csv_outfile: str
    """

    log.info(f"[yellow]Writing: {csv_outfile}")

    reduced_df = repository_df[SHORTEN_COLUMNS]

    reduced_df.to_csv(csv_outfile, index=False)
    log.info(f"[dark_green]Wrote: {csv_outfile}!")
