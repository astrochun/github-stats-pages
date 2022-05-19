from datetime import datetime as dt, timedelta as td
from math import pi
from pathlib import Path
import shutil
from typing import Dict, List, Tuple, Optional

# API related
from github import Github, UnknownObjectException
import markdown

from bokeh.plotting import figure
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, VBar
from bokeh.embed import components
from jinja2 import Environment, FileSystemLoader
import pandas as pd

from .logger import app_log as log

prefix = "merged"
stats_type = ["traffic", "clone", "referrer"]
columns = ["repository_name", "date", "total", "unique"]
r_columns = ["repository_name", "source", "total", "unique"]  # For referrer

TOOLTIPS = [
    ("index", "$index"),
    ("(x,y)", "($x, $top)"),
]

main_p = Path(__file__).parent


def load_data(data_dir: str) -> Dict[str, pd.DataFrame]:
    """
    Load stats CSV as dict of pandas DataFrame

    :param data_dir: Path containing merged*.csv
    :return: Dict of pandas DataFrame
    """

    p = Path(data_dir) / "data"

    dict_df = {}

    for stats in stats_type:
        stat_file = p / f"{prefix}_{stats}.csv"
        names = r_columns if stats == "referrer" else columns
        dict_df[stats] = pd.read_csv(stat_file, header=None, names=names)

    return dict_df


def get_date_range(df_list: List[pd.DataFrame]) -> Optional[Tuple[dt, dt]]:
    """
    Get a complete date range from clone and traffic data

    :param df_list: List of pandas DataFrame for each repository

    :return: Range of datetime
    """
    x_min = []
    x_max = []
    for df in df_list:
        date_list = [dt.strptime(d, "%Y-%m-%d") for d in df["date"]]
        if len(date_list) > 0:
            x_min.append(min(date_list))
            x_max.append(max(date_list))

    if len(x_min) > 0:
        return min(x_min) - td(days=1), max(x_max) + td(days=1)
    else:
        return None


def date_subplots(
    df: pd.DataFrame,
    y_column: str,
    date_range: tuple,
    title: str = "",
    pw: int = 350,
    ph: int = 350,
    bc: str = "#f0f0f0",
    bfc: str = "#fafafa",
) -> figure():
    """
    Generate subplots with date x-axis

    :param df: DataFrame of traffic or clone data
    :param y_column: DataFrame column to plot on y-axis, e.g. 'total', 'unique'
    :param date_range: Minimum and maximum datetime object for ``x_range``
    :param title: Title of plot
    :param pw: plot width in pixel
    :param ph: plot height in pixel
    :param bc: background color, #f0f0f0
    :param bfc: background filled color. Default: #fafafa
    """
    s = figure(
        plot_width=pw,
        plot_height=ph,
        title=title,
        background_fill_color=bc,
        border_fill_color=bfc,
        x_axis_type="datetime",
        x_range=date_range,
        tooltips=TOOLTIPS,
        tools="xpan,xwheel_zoom,xzoom_in,xzoom_out,hover,save,reset",
    )
    # s.toolbar.active_inspect = [HoverTool()]

    s.axis.major_tick_in = 6
    s.axis.major_tick_out = 0
    s.axis.minor_tick_line_color = None
    s.grid.grid_line_color = "#ffffff"

    x = [dt.strptime(d, "%Y-%m-%d") for d in df["date"]]
    y = df[y_column]
    g_source = ColumnDataSource(data={"x": x, "top": y})
    glyphs = VBar(
        x="x",
        top="top",
        bottom=0,
        width=td(days=1),
        fill_color="#f8b739",
        fill_alpha=0.8,
        line_color=None,
    )
    s.add_glyph(g_source, glyphs)
    # s.vbar(x=x, top=y, width=5.0)
    s.xaxis.formatter = DatetimeTickFormatter(years=["%Y %m"])

    return s


def refer_subplots(
    df: pd.DataFrame,
    y_column: str,
    title: str = "",
    pw: int = 350,
    ph: int = 350,
    bc: str = "#f0f0f0",
    bfc: str = "#fafafa",
) -> figure():
    """
    Generate subplots with referrer x-axis

    :param df: DataFrame of referrer data
    :param y_column: DataFrame column to plot on y-axis, e.g. 'total', 'unique'
    :param title: Title of plot
    :param pw: plot width in pixel
    :param ph: plot height in pixel
    :param bc: background color, #f0f0f0
    :param bfc: background filled color. Default: #fafafa
    """

    x = df["source"].to_list()

    s = figure(
        plot_width=pw,
        plot_height=ph,
        title=title,
        background_fill_color=bc,
        border_fill_color=bfc,
        x_range=x,
        tools="",
        toolbar_location=None,
    )

    s.axis.major_tick_in = 6
    s.axis.major_tick_out = 0
    s.xaxis.major_label_orientation = 0.83 * pi / 2
    s.axis.minor_tick_line_color = None

    s.grid.grid_line_color = "#ffffff"

    y = df[y_column]
    s.vbar(
        x=x,
        top=y,
        width=0.9,
        fill_color="#f8b739",
        fill_alpha=0.8,
        line_color=None,
    )

    return s


def user_readme(username: str, token: str = None) -> str:
    """
    Retrieve user README.md and return HTML content

    :param username: GitHub username or organization
    :return: Markdown -> HTML content
    """

    g = Github(token)
    try:
        readme_repo = g.get_repo(f"{username}/{username}")
        file_content = readme_repo.get_contents("README.md")

        readme_html = markdown.markdown(
            file_content.decoded_content.decode("utf-8"),
            extensions=[
                "sane_lists",
                "markdown.extensions.tables",
            ],
        )
    except UnknownObjectException:
        readme_html = ""

    return readme_html


def make_plots(
    username: str,
    data_dir: str,
    out_dir: str,
    csv_file: str,
    symlink: bool = False,
    token: str = "",
    include_repos: str = "",
    exclude_repos: str = "",
):
    """
    Generate HTML pages containing Bokeh plots

    :param username: GitHub username or organization
    :param data_dir: Path to working folder. CSVs are under a 'data' sub-folder
    :param out_dir: Location of outputted HTML
    :param csv_file: CSV file containing user or organization repository list
    :param symlink: Symbolic link styles assets instead of copy. Default: copy
    :param token: GitHub Personal Access Token (this is to avoid rate limits)
    :param include_repos: Repositories to only generate HTML pages.
                          Ignore csv_file inputs. Comma separated for multiples
    :param exclude_repos: Repositories to exclude from csv_file list.
                          Comma separated for more than one
    """

    if include_repos and exclude_repos:
        raise ValueError(
            "Cannot provide include_repos and exclude_repos simultaneously!"
        )

    repository_df = pd.read_csv(csv_file, converters={"description": str})
    repository_df = repository_df.loc[
        (~repository_df["fork"]) & (~repository_df["archived"])
    ]

    dict_df = load_data(data_dir)

    # Add repo folder for all static repo pages
    p_repos = Path(out_dir) / "repos"
    if not p_repos.exists():
        p_repos.mkdir(parents=True)

    # Get unique repository names
    repo_names0 = set()
    for key, df in dict_df.items():
        repo_names0.update(set(df[columns[0]].unique()))

    repo_names = set(repository_df["name"]) & repo_names0

    # Additional cleaning up:
    clean_up = repo_names0 - set(repository_df["name"])
    if len(clean_up) != 0:
        for clean in clean_up:
            p_exclude = Path(p_repos / f"{clean}.html")
            log.info(f"Deleting: {p_exclude}")
            if p_exclude.exists():
                p_exclude.unlink()

    final_repo_names = get_final_repo_names(
        p_repos,
        repo_names,
        include_repos=include_repos,
        exclude_repos=exclude_repos,
    )

    n_final_repo_names = len(final_repo_names)
    log.info(f"Number of GitHub repositories: {n_final_repo_names}")

    traffic_df = dict_df["traffic"]
    clone_df = dict_df["clone"]
    referrer_df = dict_df["referrer"]

    pw = 450  # plot width
    ph = 350  # plot height
    bc = "#f0f0f0"  # background color
    bfc = "#fafafa"  # border fill color

    # Retrieve README.md file for user
    readme_html = user_readme(username, token=token)

    avatar_response, jinja_dict = get_jinja_dict(
        username, token, final_repo_names, readme_html
    )

    # Write HTML Files
    template_p = main_p / "templates"
    file_loader = FileSystemLoader(template_p)
    env = Environment(loader=file_loader)

    write_common_html(env, jinja_dict, out_dir)

    # Copy or symlink files
    source = template_p / "styles"
    target = Path(out_dir) / "styles"
    if target.exists():
        if target.is_symlink():
            log.info("styles folder is already a symbolic link!")
        else:
            # Delete content to start fresh
            log.info("[yellow]Deleting styles assets (fresh start)")
            shutil.rmtree(target)

    if not target.exists() and not symlink:
        shutil.copytree(
            source, target, symlinks=True, copy_function=shutil.copy2
        )
    else:
        if not target.is_symlink():
            target.symlink_to(source)

    for r in final_repo_names:
        t_r_df = repository_df.loc[repository_df["name"] == r]

        if len(t_r_df) == 0:
            log.warning(
                f"[bold red]Possible issue with repository name, {r}.\n"
                f"If you renamed it, you will need to update data/ contents"
            )
        else:
            r_traffic_df = traffic_df.loc[traffic_df[columns[0]] == r]
            r_clone_df = clone_df.loc[clone_df[columns[0]] == r]
            r_referrer_df = referrer_df.loc[referrer_df[columns[0]] == r]

            date_range = get_date_range([r_traffic_df, r_clone_df])

            subplots_dict = dict(pw=pw, ph=ph, bc=bc, bfc=bfc)

            # Plot traffic data
            s1a = date_subplots(
                r_traffic_df,
                "total",
                date_range,
                "Total Daily Traffic",
                **subplots_dict,
            )

            s1b = date_subplots(
                r_traffic_df,
                "unique",
                date_range,
                "Unique Daily Traffic",
                **subplots_dict,
            )

            # Plot clones traffic
            s2a = date_subplots(
                r_clone_df,
                "total",
                date_range,
                "Total Daily Clones",
                **subplots_dict,
            )

            s2b = date_subplots(
                r_clone_df,
                "unique",
                date_range,
                "Unique Daily Clones",
                **subplots_dict,
            )

            s3a = refer_subplots(
                r_referrer_df, "total", "Total Referrals", **subplots_dict
            )

            s3b = refer_subplots(
                r_referrer_df, "unique", "Unique Referrals", **subplots_dict
            )

            grid = gridplot(
                [[s1a, s1b], [s2a, s2b], [s3a, s3b]],
                plot_width=pw,
                plot_height=ph,
            )

            script, div = components(grid)

            jinja_dict = {
                "username": username,
                "title": f"GitHub Statistics for {r}",
                "Total_Views": r_traffic_df["total"].sum(),
                "Total_Clones": r_clone_df["total"].sum(),
                "script": script,
                "div": div,
                "repos": sorted(final_repo_names),
                "avatar_url": avatar_response["avatar_url"],
            }
            jinja_dict.update(t_r_df.to_dict(orient="records")[0])

            t = env.get_template("page.html")

            out_file = p_repos / f"{r}.html"
            with open(out_file, "w") as f:
                f.writelines(t.render(jinja_dict=jinja_dict))


def get_final_repo_names(
    p_repos: Path,
    repo_names: set,
    include_repos: str = "",
    exclude_repos: str = "",
) -> set:
    """
    Filter for repositories that are specifically included/excluded

    :param p_repos: Path to repository folder
    :param repo_names: Set of all user/organization's repositories
    :param include_repos: Comma-separated list of repositories to include
    :param exclude_repos: Comma-separated list of repositories to exclude

    :return: Final repository set
    """
    final_repo_names = repo_names.copy()

    # Filter for only inclusion
    if include_repos:
        log.info(f"Only including: {include_repos.replace(',', ', ')}")
        final_repo_names = repo_names & set(include_repos.split(","))

    # Filter for exclusion
    if exclude_repos:
        log.info(f"Excluding: {exclude_repos.replace(',', ', ')}")
        final_repo_names = repo_names - set(exclude_repos.split(","))

        for exclude in exclude_repos.split(","):
            p_exclude = Path(p_repos / f"{exclude}.html")
            log.info(f"Deleting: {p_exclude}")
            if p_exclude.exists():
                p_exclude.unlink()

    return final_repo_names


def get_jinja_dict(
    username: str, token: str, final_repo_names: set, readme_html: str
) -> Tuple[dict, dict]:
    """
    Provides a dictionary for Jinja templating

    :param username: GitHub username or organization
    :param token: GitHub Personal Access Token (this is to avoid rate limits)
    :param final_repo_names: List of working GitHub repository name
    :param readme_html: Contains user README profile

    :return: Avatar JSON, Jinja dict
    """

    g = Github(token)
    gu = g.get_user(username)
    avatar_response = gu.raw_data

    jinja_dict = {
        "username": username,
        "avatar_url": avatar_response["avatar_url"],
        "repos": sorted(final_repo_names),
        "readme_html": readme_html,
    }
    return avatar_response, jinja_dict


def write_common_html(env: Environment, jinja_dict: dict, out_dir: str):
    """
    Write index, about, and repositories HTML

    :param env: Jinja Environment
    :param jinja_dict: Dictionary for jinja templating
    :param out_dir: Output file path directory
    """

    for file in ["index", "about", "repositories"]:
        t_index = env.get_template(f"{file}.html")
        out_file = Path(out_dir) / f"{file}.html"
        with open(out_file, "w") as f:
            f.writelines(t_index.render(jinja_dict=jinja_dict))
