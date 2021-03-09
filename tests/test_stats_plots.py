from pathlib import Path
from github_stats_pages import stats_plots

tests_data_folder = Path('tests_data')


def test_load_data():
    dict_df = stats_plots.load_data(tests_data_folder)
    assert isinstance(dict_df, dict)


def test_make_plots(username):
    d0 = {
        'username': username,
        'data_dir': tests_data_folder,
        'out_dir': tests_data_folder,
        'csv_file': tests_data_folder / 'repository.csv',
    }
    stats_plots.make_plots(**d0)

    for html_file in ['index.html', 'about.html', 'github-stats-pages.html']:
        p = tests_data_folder / html_file
        assert p.exists()
        p.unlink()
