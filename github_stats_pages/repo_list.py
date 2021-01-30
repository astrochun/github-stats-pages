from typing import Tuple
import requests
import json
import pandas as pd

SHORTEN_COLUMNS = ['id', 'name', 'html_url', 'description', 'language',
                   'fork', 'stargazers_count', 'watchers_count', 'has_issues',
                   'has_downloads', 'has_wiki', 'has_pages', 'forks_count',
                   'disabled', 'open_issues_count', 'license', 'forks',
                   'open_issues', 'watchers', 'default_branch']


def get_repo_list(user: str) -> Tuple[list, pd.DataFrame]:
    """
    Get list of public repository for a give user

    :param user: GitHub user or organization handle (e.g., "numpy")

    :return repository_list: List of public repositories and additional info
    :return repository_df: DataFrame containing public repositories
    """

    endpoint = f"https://api.github.com/users/{user}/repos"

    params = {
        'per_page': 100
    }

    response = requests.get(endpoint, params=params)
    repository_list = json.loads(response.content)

    repository_df = pd.DataFrame.from_dict(repository_list)

    return repository_list, repository_df


def construct_csv(repository_df: pd.DataFrame, csv_outfile: str):
    """
    Write CSV file with repository information

    :param repository_df: DataFrame containing results (see get_repo_list)
    :type repository_df: pandas.core.frame.DataFrame

    :param csv_outfile: Filename for output file
    :type csv_outfile: str
    """

    reduced_df = repository_df[SHORTEN_COLUMNS]

    print(f"Writing: {csv_outfile}")
    reduced_df.to_csv(csv_outfile, index=False)
