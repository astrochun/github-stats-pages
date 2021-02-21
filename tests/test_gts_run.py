from github_stats_pages import gts_run

username = 'astrochun'

filename = f'{username}.csv'


def test_run_all_repos(token):
    gts_run.run_all_repos(username, token, filename, save_csv=False)
