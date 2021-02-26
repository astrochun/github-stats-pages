from pathlib import Path
from github_stats_pages import gts_run

username = 'astrochun'


def test_run_each_repo(token):
    gts_run.run_each_repo(username, token, 'github-stats-pages', save_csv=False)
    assert list(Path('.').glob('*stats.csv')) == []

    gts_run.run_each_repo(username, token, 'github-stats-pages', save_csv=True)
    assert len(list(Path('.').glob('*stats.csv'))) == 3
