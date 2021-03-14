# github-stats-pages
Retrieve statistics for a user's repositories and populate the information onto a GitHub static page

[![GitHub Workflow Status (main)](https://img.shields.io/github/workflow/status/astrochun/github-stats-pages/Python%20package/main?color=blue&label=build%20%28main%29&logo=github)](https://github.com/astrochun/github-stats-pages/actions?query=workflow%3A%22Python+package%22+branch%3Amain)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/astrochun/github-stats-pages/Python%20package?color=blue&label=build%20%28latest%29&logo=github)](https://github.com/astrochun/github-stats-pages/actions?query=workflow%3A%22Python+package%22)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/github-stats-pages)
[![PyPI](https://img.shields.io/pypi/v/github-stats-pages?color=blue)](https://pypi.org/project/github-stats-pages)

![PyPI - Downloads](https://img.shields.io/pypi/dm/github-stats-pages?color=light%20green&label=PyPI-download)

- [Overview](#overview)
- [Installation](#installation)
- [Execution](#execution)
- [Versioning](#versioning)
- [Continuous Integration](#continuous-integration)
- [Authors](#authors)
- [License](#license)

## Overview

## Installation

Use our [PyPI package](https://pypi.org/project/github-traffic-stats/) to
get the most stable release:
```
(venv) $ pip install github-stats-pages
```

Or if you want the latest version then:
```
(venv) $ git clone https://github.com/astrochun/github-stats-pages
(venv) $ cd github-stats_pages
(venv) $ python setup.py install
```

## Execution

There are four primary scripts accompanying `github-stats-pages`
1. `get_repo_list`
2. `gts_run_all_repos`
3. `merge-csv.sh`
3. `make_stats_plots`

`get_repo_list` generates a CSV file containing a list of public repositories
for a GitHub user/organization. This database allows the code to aggregate
statistics  for all repositories. To run, simply use the following command:

```
(venv) laptop:github_data $ get_repo_list -u <username/organization>
```

This will generate a CSV file called "<username/organization>.csv".
It is recommended to create a folder (e.g., `github_data`) as the contents
will ultimately contain multiple files.

Next, let's gather the statistics for all public repositories that are not
forks. We use another Python library that does this called
[github-traffic-stats](https://github.com/nchah/github-traffic-stats). It
is accompanied by a `python` script called `gts`.

To access traffic data, this requires a
[Personal Access Token (PAT)](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token),
so let's create a PAT. Generate one by going to the
[following GitHub page](https://github.com/settings/tokens).
For selected scopes you will only need `repo`.

Then you can execute the next script:

```
(venv) laptop:github_data $ API_TOKEN='abcdef12345678'
(venv) laptop:github_data $ gts_run_all_repos -u <username/organization> -t $API_TOKEN -c <username/organization>.csv
```

This will generate CSV files with date and time stamps prefixes for clones,
traffic, and referrals. With routine running of this code, you will
generate additional CSV files that allow for you to extend beyond a two-week
window of data aggregation. The data can be merged with the `merge-csv.sh`
script:

```
(venv) laptop:github_data $ ./merge-csv.sh
```

This generates three files: merge_clones.csv, merge_traffic.csv and
merge_referrers.csv. These files are used in the final step to generate the
plots.

Finally to generate static pages containing the visualization, we
use the `make_stats_plots` script:

```
(venv) laptop:github_data $ make_stats_plots -u <username> -c <username>.csv
```

This will generate all contents in the local path. Note that you can specify
an output directory with the `-o`/`--out-dir` option.

## Versioning

## Continuous Integration

## Authors

* Chun Ly, Ph.D. ([@astrochun](http://www.github.com/astrochun))

See also the list of
[contributors](https://github.com/astrochun/github-stats-pages/contributors) who participated in this project.


## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT) - see the [LICENSE](LICENSE) file for details.