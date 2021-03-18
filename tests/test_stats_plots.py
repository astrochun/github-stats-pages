import shutil
import os
from pathlib import Path

from github_stats_pages import stats_plots

tests_data_folder = Path('tests_data')


def test_load_data():
    dict_df = stats_plots.load_data(tests_data_folder, ci=True)
    assert isinstance(dict_df, dict)


def test_make_plots(username):
    d0 = {
        'username': username,
        'data_dir': tests_data_folder,
        'out_dir': tests_data_folder,
        'csv_file': tests_data_folder / 'repository.csv',
    }
    stats_plots.make_plots(**d0, ci=True)

    for html_file in ['index.html', 'about.html', 'github-stats-pages.html']:
        p = tests_data_folder / html_file
        assert p.exists()
        p.unlink()

    # Test folder and symlink
    stats_plots.make_plots(**d0, ci=True)  # check that folder is clean and restarted

    stats_plots.make_plots(**d0, symlink=True, ci=True)

    stats_plots.make_plots(**d0, ci=True)

    os.unlink(tests_data_folder / "styles")
