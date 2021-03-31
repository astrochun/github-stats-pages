import os
from pathlib import Path

import pytest

from github_stats_pages import stats_plots

tests_data_folder = Path('tests_data')


def test_load_data():
    dict_df = stats_plots.load_data(tests_data_folder)
    assert isinstance(dict_df, dict)


def test_make_plots(username, token):
    def html_check(input_list: list, exists=True):
        for html_file in input_list:
            p = tests_data_folder / html_file
            if exists:
                assert p.exists()
                p.unlink()  # Delete file for clean set-up
            else:
                assert not p.exists()

    d0 = {
        'username': username,
        'token': token,
        'data_dir': tests_data_folder,
        'out_dir': tests_data_folder,
        'csv_file': tests_data_folder / 'repository.csv',
    }
    html_list = ['index.html', 'about.html', 'repositories.html',
                 'repos/github-stats-pages.html']

    # General test
    stats_plots.make_plots(**d0)

    html_check(html_list)

    # Check that folder is clean and restarted
    stats_plots.make_plots(**d0)

    # Test for symlink case. Delete static assets and create symlink
    stats_plots.make_plots(**d0, symlink=True)

    # Delete styles assets if exists
    stats_plots.make_plots(**d0)

    d2 = d0.copy()
    d2.update({'exclude_repos': 'github-stats-pages'})
    stats_plots.make_plots(**d2)

    html_check(html_list[:-1])
    html_check([html_list[-1]], exists=False)  # Check that github-stats-pages.html does not exist

    d3 = d0.copy()
    d3.update({'include_repos': 'github-stats-pages'})
    stats_plots.make_plots(**d3)

    html_check(html_list)

    # Check error when both exclude_repos and include_repos are included
    d4 = d2.copy()
    d4.update({'include_repos': 'github-stats-pages'})
    with pytest.raises(ValueError):
        stats_plots.make_plots(**d4)

    # Clean up after unit test run
    Path(tests_data_folder / "styles").unlink()
    for file in html_list:
        p_file = Path(f"{tests_data_folder}/{file}")
        if p_file.exists():
            p_file.unlink()

    os.rmdir(f"{tests_data_folder}/repos")  # Delete repos folder

    # Delete gts csv files
    test_csv_files = Path('').glob('????-??-??-???-???-*stats.csv')
    for delete_file in list(test_csv_files):
        delete_file.unlink()
