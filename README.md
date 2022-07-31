# github-stats-pages
Retrieve statistics for a user's repositories and populate the information onto a GitHub static page

| Categories | Status                                                                                                                                                                                                                                                                                                                                                                                                                                             |
|------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| General    | ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/github-stats-pages) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)                                                                                                                                                                                                                                               |
| CI/CD      | [![GitHub Workflow Status](https://img.shields.io/github/workflow/status/astrochun/github-stats-pages/Python%20package/main?color=blue&label=build&logo=github)](https://github.com/astrochun/github-stats-pages/actions?query=workflow%3A%22Python+package%22+branch%3Amain) ![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/wiki/astrochun/github-stats-pages/python-coverage-comment-action-badge.json) |
| PyPI       | [![PyPI](https://img.shields.io/pypi/v/github-stats-pages?color=blue)](https://pypi.org/project/github-stats-pages) ![PyPI - Downloads](https://img.shields.io/pypi/dm/github-stats-pages?color=light%20green&label=PyPI-download)                                                                                                                                                                                                                 |

- [Overview](#overview)
- [Requirements](#requirements)
- [Deployment](#deployment)
   - [GitHub Actions Deployment](#github-actions-deployment)
   - [Docker Deployment](#docker-deployment)
   - [From Source](#from-source)
- [Installation](#installation)
- [Execution](#execution)
- [FAQ](#faq)
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
For scopes, select: `repo`. Save your PAT in a safe place as you will need it later.

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
3. If not already enabled, enable GitHub Actions (Settings > Actions)
4. Sit back and enjoy that ☕️ !

Note: After the first Action run, you may need to enable GitHub pages through
the  settings page and select `gh-pages` (Settings > Pages)

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
    env:
      BOT_NAME: 'github-actions[bot]'
      BOT_EMAIL: '41898282+github-actions[bot]@users.noreply.github.com'

    steps:
    - name: Checkout
      uses: actions/checkout@v2
    - name: Get current date
      id: date
      run: echo "::set-output name=date::$(date +'%Y-%m-%d')"
    - name: Build GitHub stats pages
      uses: astrochun/github-stats-pages@latest
      with:
        username: ${{ github.repository_owner }}
        token: ${{ secrets.GH_TOKEN }}
    - name: Upload data to main branch
      uses: EndBug/add-and-commit@v7.0.0
      with:
        add: 'data'
        branch: main
        message: "Update data: ${{ steps.date.outputs.date }}"
        author_name: env.BOT_NAME
        author_email: env.BOT_EMAIL
    - name: Upload static files to gh-pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        personal_token: ${{ secrets.GH_TOKEN }}
        publish_dir: ./public
        keep_files: false
        user_name: env.BOT_NAME
        user_email: env.BOT_EMAIL
        publish_branch: gh-pages
        commit_message: "Update static pages: ${{ steps.date.outputs.date }}"
```

This workflow will run for all public repositories.

##### Inputs

| Variable        | Description                                                                                | Required? | Type  | Defaults | Examples                                   |
|-----------------|--------------------------------------------------------------------------------------------|-----------|-------|----------|--------------------------------------------|
| `username`      | GitHub username or organization                                                            | **Yes**   | `str` | N/A      | `astrochun`                                |
| `token`         | GitHub Personal Access Token (PAT)                                                         | **Yes**   | `str` | N/A      | `abcdef12345678`                           |
| `include-repos` | Comma-separated lists of repositories. This overrides the full list of public repositories | No        | `str` | `''`     | `'github-stats-pages,astrochun.github.io'` |
| `exclude-repos` | Comma-separated lists of repositories to exclude from default public repository list       | No        | `str` | `''`     | `'repo1'`                                  |

##### Other GitHub Action deployment examples:

To override all public repositories and limit to a subset of public repositories,
specify a comma-separated list (_no spaces between commas_) for `include-repos` argument.

```yaml
    - name: Build GitHub stats pages
      uses: astrochun/github-stats-pages@latest
      with:
        username: ${{ github.repository_owner }}
        token: ${{ secrets.GH_TOKEN }}
        include-repos: "github-stats-pages"
```

Alternatively to exclude specific repositories from the list of public repositories,
use the `exclude-repos` argument with a comma-separated list (_no spaces between commas_).

```yaml
    - name: Build GitHub stats pages
      uses: astrochun/github-stats-pages@latest
      with:
        username: ${{ github.repository_owner }}
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
3. `make_stats_plots`
4. `merge_csv`

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
(venv) laptop:github_data $ merge_csv
```

This generates four files: merged_clone.csv, merged_paths.csv, merged_referrers.csv,
and merge_traffic.csv. These files are used in the final step to generate the
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
│   ├── merged_paths.csv
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

## FAQ

### 1. How do I add old data?

If you ran this code outside your production deployment (e.g., GitHub pages),
it is in fact straightforward to include those data.

For GitHub Pages deployment, simply:
   1. `git clone` your copy of the [`github-stats`](https://github.com/astrochun/github-stats) repo
   2. Move/copy previous CSV files to the `data` folder in the `main` branch.
      These files follow a YYYY-MM-DD prefix
   3. Then add, commit, and push:
      `git add data/????-??-??*stats.csv`, `git commit -m "Add old data"`, `git push`

On the next GitHub Action scheduled run, the live pages will automatically incorporate these data.

For any other deployments (e.g., cloud), simply:
   1. Move/copy/`rsync`/`scp` the previous CSV files to the `data` folder in the deployed instance

Upon the next `cronjob` or script run, the old data will automatically be incorporated.

### 2. How do I add content to the home page (`index.html`)?

The deployed `index.html` can be customized to provide a biography, cool
graphics, and/or additional statistics. This is possible through a
[GitHub profile README](https://docs.github.com/en/github/setting-up-and-managing-your-github-profile/managing-your-profile-readme)
that you can create. The link above provides instruction for setting up one. This software
will convert the markdown content to HTML and include it in the `index.html`.
An example of the outcome can be found [here](https://astrochun.github.io/github-stats/).

Many GitHub users have developed fancy GitHub profile READMEs:
[https://github.com/abhisheknaiidu/awesome-github-profile-readme](https://github.com/abhisheknaiidu/awesome-github-profile-readme).
By including those in your profile README, they should be included in your deployed version.
If it doesn't work, feel free to reach out.

Note: While a GitHub profile README does not work for an organization in the same manner as
individual GitHub accounts, this software will still use its content if it is publicly available.
Here's an [example](https://ual-odis.github.io/github-stats/)

### 3. What happens when I renamed a repository?

This software will retrieve the latest list of public repositories. When the
statistics pages are then generated, it searches the `data/` folder for the
information for each repo. As such, there is an issue with renaming of
repositories. This will be apparent in the logs with the following warnings:
```
WARNING: Possible issue with repository name, ...
If you renamed it, you will need to update data/ contents
```

To rectify this issue, you can `git clone` your GitHub repository, and rename
each occurrence of the old repositories with the new ones using your preferred
IDE or command-line options (e.g., `sed`). Then `git add`, `git commit`, and
`git push` these changes. The next scheduled run will then work as intended.

## Versioning

## Continuous Integration

## Authors

* Chun Ly, Ph.D. ([@astrochun](http://www.github.com/astrochun))

See also the list of
[contributors](https://github.com/astrochun/github-stats-pages/contributors) who participated in this project.


## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT) - see the [LICENSE](LICENSE) file for details.


## Used by

A list of repos using `github-stats-pages` can be found [here](https://github.com/topics/github-stats-pages).

<!-- start: readme-repos-list -->
<!-- This list is auto-generated using koj-co/readme-repos-list -->
<!-- Do not edit this list manually, your changes will be overwritten -->
[![astrochun/test-stats](https://images.weserv.nl/?url=avatars.githubusercontent.com%2Fu%2F20305734%3Fv%3D4&h=50&w=50&fit=cover&mask=circle&maxage=7d)](https://github.com/astrochun/test-stats)
[![hessevans/test1](https://images.weserv.nl/?url=avatars.githubusercontent.com%2Fu%2F85516139%3Fv%3D4&h=50&w=50&fit=cover&mask=circle&maxage=7d)](https://github.com/hessevans/test1)
[![schorschinho/github-stats-osprey](https://images.weserv.nl/?url=avatars.githubusercontent.com%2Fu%2F16669943%3Fv%3D4&h=50&w=50&fit=cover&mask=circle&maxage=7d)](https://github.com/schorschinho/github-stats-osprey)
[![UAL-RE/github-stats](https://images.weserv.nl/?url=avatars.githubusercontent.com%2Fu%2F61063507%3Fv%3D4&h=50&w=50&fit=cover&mask=circle&maxage=7d)](https://UAL-RE.github.io/github-stats)
[![thenomaniqbal/thenomaniqbal](https://images.weserv.nl/?url=avatars.githubusercontent.com%2Fu%2F45229497%3Fv%3D4&h=50&w=50&fit=cover&mask=circle&maxage=7d)](https://github.com/thenomaniqbal/thenomaniqbal)
[![Mo-Shakib/Mo-Shakib](https://images.weserv.nl/?url=avatars.githubusercontent.com%2Fu%2F50780268%3Fv%3D4&h=50&w=50&fit=cover&mask=circle&maxage=7d)](https://github.com/Mo-Shakib/Mo-Shakib)
<!-- end: readme-repos-list -->
