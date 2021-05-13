from pathlib import Path
from github_stats_pages import gts_run


def test_run_each_repo(username, token):
    gts_run.run_each_repo(username, token, 'github-stats-pages', save_csv=False)
    assert list(Path('.').glob('*stats.csv')) == []

    gts_run.run_each_repo(username, token, 'github-stats-pages', save_csv=True)
    p0 = Path('.').glob('*stats.csv')
    assert len(list(p0)) == 3
    for file in p0:
        Path(file).unlink()


def test_get_popular_content(username, token):
    for save in [False, True]:
        gts_run.get_top_paths(username, token, 'github-stats-pages',
                              save_csv=save)
