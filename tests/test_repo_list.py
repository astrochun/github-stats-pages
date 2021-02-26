import pandas as pd
from os.path import exists

from github_stats_pages import repo_list

username = 'astrochun'


def test_get_repo_list():

    repository_list, repository_df = repo_list.get_repo_list(username)

    assert isinstance(repository_list, list)
    assert isinstance(repository_df, pd.DataFrame)

    repo_list.construct_csv(repository_df, f"{username}.csv")
    assert exists(f"{username}.csv")
