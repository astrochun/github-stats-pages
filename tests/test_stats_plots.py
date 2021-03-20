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

    for html_file in ['index.html', 'about.html', 'repositories.html',
                      'repos/github-stats-pages.html']:
        p = tests_data_folder / html_file
        assert p.exists()
        p.unlink()

    # Test folder and symlink
    stats_plots.make_plots(**d0, ci=True)  # check that folder is clean and restarted

    stats_plots.make_plots(**d0, symlink=True, ci=True)

    stats_plots.make_plots(**d0, ci=True)

    # Clean up after unit test run
    Path(tests_data_folder / "styles").unlink()
    for html_file in ['index.html', 'about.html', 'repositories.html',
                      'repos/github-stats-pages.html']:
        Path(f"{tests_data_folder}/{html_file}").unlink()

    os.rmdir(f"{tests_data_folder}/repos")  # Delete repos folder

    # Delete gts csv files
    test_csv_files = Path('').glob('????-??-??-???-???-*stats.csv')
    for delete_file in list(test_csv_files):
        delete_file.unlink()
