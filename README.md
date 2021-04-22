# github-stats-pages
Retrieve statistics for a user's repositories and populate the information onto a GitHub static page

[![GitHub Workflow Status (main)](https://img.shields.io/github/workflow/status/astrochun/github-stats-pages/Python%20package/main?color=blue&label=build%20%28main%29&logo=github)](https://github.com/astrochun/github-stats-pages/actions?query=workflow%3A%22Python+package%22+branch%3Amain)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/astrochun/github-stats-pages/Python%20package?color=blue&label=build%20%28latest%29&logo=github)](https://github.com/astrochun/github-stats-pages/actions?query=workflow%3A%22Python+package%22)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/github-stats-pages)
[![PyPI](https://img.shields.io/pypi/v/github-stats-pages?color=blue)](https://pypi.org/project/github-stats-pages)

![PyPI - Downloads](https://img.shields.io/pypi/dm/github-stats-pages?color=light%20green&label=PyPI-download)

- [Overview](#overview)
- [Requirements](#requirements)
- [Deployment](#deployment)
   - [GitHub Actions Deployment](#github-actions-deployment)
   - [Docker Deployment](#docker-deployment)
   - [From Source](#from-source)
- [Installation](#installation)
- [Execution](#execution)
- [Versioning](#versioning)
- [Continuous Integration](#continuous-integration)
- [Authors](#authors)
- [License](#license)
- [Used by](#used-by)

## Overview

This software is both a GitHub Docker container action and a Python
packaged software. The former allows for this to run to generate GitHub
pages while the latter gives flexibility to deploy on a variety of
compute resources (e.g., cloud, dev).

Some key features of this software:

1. Flexible - Designed to be deployed in a number of ways
2. Python - Most of the code is Python (excluding static assets) with static types
3. Copy-left license: This is supported by open source and thus is open source
   with an MIT License!
4. Continuous Integration - We currently have 100% code coverage of the Python
   codebase and the Docker action
5. Environmentally friendly - [Websitecarbon.com](https://www.websitecarbon.com/)
   reported that a GitHub Pages deployment of this code has a lower carbon
   footprint than 90% of web pages tested

## Requirements

[Traffic data](https://docs.github.com/en/github/visualizing-repository-data-with-graphs/viewing-traffic-to-a-repository)
for repositories are limited to those who have write or ownership access.
Thus, regardless of how you choose to deploy, you will need a token.
This codebase uses
[GitHub's Personal Access Token (PAT)](https://github.blog/2013-05-16-personal-api-tokens/).

To create one, follow these
[instructions](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token)
or go [here](https://github.com/settings/tokens).
For scopes, select: `repo` and `workflow` (if you decide to deploy using GitHub Action).
Save your PAT in a safe place as you will provide it below.

## Deployment

This code is intended to deploy in a number of ways to allow for the greatest flexibility.
First, this repository is also as a
[GitHub Docker container action](https://docs.github.com/en/actions/creating-actions/about-actions#docker-container-actions) (see [below](#github-actions-deployment)).
Second, this code is package on [PyPI](https://pypi.org/project/github-stats-pages/).
Third, the source code can be [forked](https://github.com/astrochun/github-stats-pages/fork)
or cloned.
Finally, a [Dockerfile](Dockerfile) is included for containerization.

### GitHub Actions Deployment

#### TL;DR

For easy deployment, try this
[GitHub template](https://github.com/astrochun/github-stats). Simply:

1. [Use it!](https://github.com/astrochun/github-stats/generate)
2. Add a Personal access token, as a repository secret, `GH_TOKEN`.
   See [above](#requirements) (Settings > Secrets)
3. Enable GitHub Actions (Settings > Actions)
4. Enable GitHub pages through the settings page and select `gh-pages`
   (Settings > Pages)
5. Sit back and enjoy that ☕️ !

#### The Nitty Gritty

GitHub Pages deployment is simple with the following GitHub Actions `cronjob` workflow:

```yaml
name: Deploy GitHub pages with traffic stats

on:
  schedule:
    - cron: "0 3 * * *"

jobs:
  build-n-publish:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout
      uses: actions/checkout@v2
    - name: Get current date
      id: date
      run: echo "::set-output name=date::$(date +'%Y-%m-%d')"
    - name: Build GitHub stats pages
      uses: astrochun/github-stats-pages@latest
      with:
        username: ${{ github.actor }}
        token: ${{ secrets.GH_TOKEN }}
    - name: Upload data to main branch
      uses: EndBug/add-and-commit@v7.0.0
      with:
        add: 'data'
        branch: main
        message: "Update data: ${{ steps.date.outputs.date }}"
        author_name: 'github-actions[bot]'
        author_email: '41898282+github-actions[bot]@users.noreply.github.com'
    - name: Upload static files to gh-pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        personal_token: ${{ secrets.GH_TOKEN }}
        publish_dir: ./public
        keep_files: false
        user_name: 'github-actions[bot]'
        user_email: '41898282+github-actions[bot]@users.noreply.github.com'
        publish_branch: gh-pages
        commit_message: "Update static pages: ${{ steps.date.outputs.date }}"
```

This workflow will run for all public repositories.

##### Inputs

| Variable        | Description                        | Required? | Type  | Defaults | Examples         |
| --------------- | ---------------------------------- | --------- | ----- | -------- | ---------------- |
| `username`      | GitHub username or organization    | **Yes**   | `str` | N/A      | `astrochun`      |
| `token`         | GitHub Personal Access Token (PAT) | **Yes**   | `str` | N/A      | `abcdef12345678` |
| `include-repos` | Comma-separated lists of repositories. This overrides the full list of public repositories | No | `str` | `''` | `'github-stats-pages,astrochun.github.io'`
| `exclude-repos` | Comma-separated lists of repositories to exclude from default public repository list | No | `str` | `''` | `'repo1'` |

##### Other GitHub Action deployment examples:

To override all public repositories and limit to a subset of public repositories,
specify a comma-separated list (_no spaces between commas_) for `include-repos` argument.

```yaml
    - name: Build GitHub stats pages
      uses: astrochun/github-stats-pages@latest
      with:
        username: ${{ github.actor }}
        token: ${{ secrets.GH_TOKEN }}
        include-repos: "github-stats-pages"
```

Alternatively to exclude specific repositories from the list of public repositories,
use the `exclude-repos` argument with a comma-separated list (_no spaces between commas_).

```yaml
    - name: Build GitHub stats pages
      uses: astrochun/github-stats-pages@latest
      with:
        username: ${{ github.actor }}
        token: ${{ secrets.GH_TOKEN }}
        exclude-repos: "repo1,repo2"
```

Note that you can only specify `include-repos` _or_ `exclude-repos`.
**Specifying both will fail**!

### Docker Deployment

This repository includes a [Dockerfile](Dockerfile).
More details/instructions provided later.

### From source

To run this code from original source, you will need to install it.

#### Installation

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

#### Execution from source

TL;DR: If you decide to run this code from source, there are a few things you should know.

First, this repository includes an [`entrypoint.sh`](entrypoint.sh).
You can simply execute it with the following:
```
(venv) laptop:github_data $ username="<username>"
(venv) laptop:github_data $ token="<personal_access_token>"
(venv) laptop:github_data $ /path/to/github-stats-pages/entrypoint.sh $username $token
```

Second, it is recommended to create a folder (e.g., `github_data`) as the contents
will ultimately contain multiple files.

#### More details

Here's an overview providing more details how this codebase works.
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

To access traffic data, this requires a PAT. See [above](#requirements)
for instructions. Then you can execute the next script:

```
(venv) laptop:github_data $ token='abcdef12345678'
(venv) laptop:github_data $ gts_run_all_repos -u <username/organization> -t $token -c <username/organization>.csv
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
(venv) laptop:github_data $ make_stats_plots -u <username> -c <username>.csv -t $token
```

This will generate all contents in the local path. Note that you can specify
an output directory with the `-o`/`--out-dir` option. Default is the current
path.

The resulting folder structure, for example, will be the following:

```
github_data/
├── data
│   ├── 2021-01-17-00h-46m-clone-stats.csv
│   ├── 2021-01-17-00h-46m-referrer-stats.csv
│   ├── 2021-01-17-00h-46m-traffic-stats.csv
│   ├── ...
│   ├── merged_clone.csv
│   ├── merged_referrer.csv
│   └── merged_traffic.csv
├── repos
│   ├── github-stats-pages.html
│   └── ...
├── styles
|   ├── css
|   │   └── style.css
|   └── js
|       ├── bootstrap.min.js
|       ├── jquery.min.js
|       ├── main.js
|       └── popper.js
├── about.html
├── index.html
├── repositories.html
└── <username>.csv
```

## Versioning

## Continuous Integration

## Authors

* Chun Ly, Ph.D. ([@astrochun](http://www.github.com/astrochun))

See also the list of
[contributors](https://github.com/astrochun/github-stats-pages/contributors) who participated in this project.


## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT) - see the [LICENSE](LICENSE) file for details.


## Used by

A list of repos using `github-stats-pages` can be found [here](https://github.com/topics/github-stats-pages)

<!-- start: readme-repos-list -->
<!-- end: readme-repos-list -->
