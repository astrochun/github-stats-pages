import shutil
from pathlib import Path
from requests import get

from typing import Dict, Union

from math import pi
import pandas as pd
from datetime import datetime as dt, timedelta as td

# Bokeh Libraries
from bokeh.plotting import figure
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, VBar  # HoverTool
from bokeh.embed import components
from jinja2 import Environment, FileSystemLoader

prefix = 'merged'
stats_type = ['traffic', 'clone', 'referrer']
columns = ['repository_name', 'date', 'total', 'unique']
r_columns = ['repository_name', 'source', 'total', 'unique']  # For referrer

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
        stat_file = p / f'{prefix}_{stats}.csv'
        names = r_columns if stats == 'referrer' else columns
        dict_df[stats] = pd.read_csv(stat_file, header=None, names=names)

    return dict_df


def date_subplots(df: pd.DataFrame, y_column: str, title: str = '',
                  pw: int = 350, ph: int = 350, bc: str = "#f0f0f0",
                  bfc: str = "#fafafa") -> figure():

    s = figure(plot_width=pw, plot_height=ph, title=title,
               background_fill_color=bc, border_fill_color=bfc,
               x_axis_type="datetime", tooltips=TOOLTIPS,
               tools="xpan,xwheel_zoom,xzoom_in,xzoom_out,hover,save,reset")
    # s.toolbar.active_inspect = [HoverTool()]

    s.axis.major_tick_in = 6
    s.axis.major_tick_out = 0
    s.axis.minor_tick_line_color = None
    s.grid.grid_line_color = "#ffffff"

    x = [dt.strptime(d, '%Y-%m-%d') for d in df['date']]
    y = df[y_column]
    g_source = ColumnDataSource(data={'x': x, 'top': y})
    glyphs = VBar(x='x', top='top', bottom=0, width=td(days=1),
                  fill_color="#f8b739", fill_alpha=0.8, line_color=None)
    s.add_glyph(g_source, glyphs)
    # s.vbar(x=x, top=y, width=5.0)
    s.xaxis.formatter = DatetimeTickFormatter(years=["%Y %m"])

    return s


def refer_subplots(df: pd.DataFrame, y_column: str, title: str = '',
                   pw: int = 350, ph: int = 350, bc: str = "#f0f0f0",
                   bfc: str = "#fafafa") -> figure():

    x = df['source'].to_list()
    '''print(x)
    s.x_range = FactorRange(*x)'''

    s = figure(plot_width=pw, plot_height=ph, title=title,
               background_fill_color=bc, border_fill_color=bfc,
               x_range=x, tools="", toolbar_location=None)

    s.axis.major_tick_in = 6
    s.axis.major_tick_out = 0
    s.xaxis.major_label_orientation = 0.83 * pi/2
    s.axis.minor_tick_line_color = None

    s.grid.grid_line_color = "#ffffff"
    # s.axis.minor_tick_in = 3
    # s.axis.minor_tick_out = 0
    # s.axis.subgroup_label_orientation = "normal"

    y = df[y_column]
    s.vbar(x=x, top=y, width=0.9, fill_color="#f8b739", fill_alpha=0.8,
           line_color=None)

    return s


def make_plots(username: str, data_dir: str, out_dir: str, csv_file: str,
               symlink: bool = False,
               include_repo: Union[str, list] = '',
               exclude_repo: Union[str, list] = ''):

    if include_repo and exclude_repo:
        raise ValueError(
            "Cannot provide include_repo and exclude_repo simultaneously!"
        )

    repository_df = pd.read_csv(csv_file)

    dict_df = load_data(data_dir)

    # Get unique repository names
    repo_names = set()
    for key, df in dict_df.items():
        repo_names.update(set(df[columns[0]].unique()))

    final_repo_names = repo_names  # init

    # Filter for only inclusion
    if include_repo:
        if isinstance(include_repo, str):
            include_repo = [include_repo]
        print(f"Only including: {', '.join(include_repo)}")
        final_repo_names = repo_names & set(include_repo)

    # Filter for exclusion
    if exclude_repo:
        if isinstance(exclude_repo, str):
            exclude_repo = [exclude_repo]
        print(f"Excluding: {', '.join(exclude_repo)}")
        final_repo_names = repo_names - set(exclude_repo)

    n_final_repo_names = len(final_repo_names)
    print(f"Number of GitHub repositories: {n_final_repo_names}")

    traffic_df = dict_df['traffic']
    clone_df = dict_df['clone']
    referrer_df = dict_df['referrer']

    pw = 450  # plot width
    ph = 350  # plot height
    bc = "#f0f0f0"  # background color
    bfc = "#fafafa"  # border fill color

    avatar_response = get(f'https://api.github.com/users/{username}').json()
    jinja_dict = {
        'username': username,
        'avatar_url': avatar_response['avatar_url'],
        'repos': sorted(final_repo_names),
    }

    # Write HTML Files
    template_p = main_p / 'templates'
    file_loader = FileSystemLoader(template_p)
    env = Environment(loader=file_loader)
    for file in ['index', 'about', 'repositories']:
        t_index = env.get_template(f"{file}.html")
        out_file = Path(out_dir) / f"{file}.html"
        with open(out_file, 'w') as f:
            f.writelines(t_index.render(jinja_dict=jinja_dict))

    # Copy or symlink files
    source = template_p / "styles"
    target = Path(out_dir) / "styles"
    if target.exists():
        if target.is_symlink():
            print("styles folder is already a symbolic link!")
        else:
            # Delete content to start fresh
            print("Deleting styles assets (fresh start) ...")
            shutil.rmtree(target)

    if not target.exists() and not symlink:
        shutil.copytree(source, target, symlinks=True,
                        copy_function=shutil.copy2)
    else:
        if not target.is_symlink():
            target.symlink_to(source)

    for r in final_repo_names:
        t_r_df = repository_df.loc[repository_df['name'] == r]

        r_traffic_df = traffic_df.loc[traffic_df[columns[0]] == r]
        r_clone_df = clone_df.loc[clone_df[columns[0]] == r]
        r_referrer_df = referrer_df.loc[referrer_df[columns[0]] == r]

        # Plot traffic data
        s1a = date_subplots(r_traffic_df, 'total', 'Total Daily Traffic', pw=pw,
                            ph=ph, bc=bc, bfc=bfc)

        s1b = date_subplots(r_traffic_df, 'unique', 'Unique Daily Traffic', pw=pw,
                            ph=ph, bc=bc, bfc=bfc)

        # Plot clones traffic
        s2a = date_subplots(r_clone_df, 'total', 'Total Daily Clones', pw=pw,
                            ph=ph, bc=bc, bfc=bfc)

        s2b = date_subplots(r_clone_df, 'unique', 'Unique Daily Clones', pw=pw,
                            ph=ph, bc=bc, bfc=bfc)

        s3a = refer_subplots(r_referrer_df, 'total', 'Total Referrals', pw=pw,
                             ph=ph, bc=bc, bfc=bfc)

        s3b = refer_subplots(r_referrer_df, 'unique', 'Unique Referrals', pw=pw,
                             ph=ph, bc=bc)

        grid = gridplot([[s1a, s1b], [s2a, s2b], [s3a, s3b]],
                        plot_width=pw, plot_height=ph)

        script, div = components(grid)

        jinja_dict = {
            'username': username,
            'title': f"GitHub Statistics for {r}",
            'Total_Views': r_traffic_df['total'].sum(),
            'Total_Clones': r_clone_df['total'].sum(),
            'script': script,
            'div': div,
            'repos': sorted(final_repo_names),
            'avatar_url': avatar_response['avatar_url'],
        }
        jinja_dict.update(t_r_df.to_dict(orient='records')[0])

        t = env.get_template('page.html')

        out_file = Path(out_dir) / f"{r}.html"
        with open(out_file, 'w') as f:
            f.writelines(t.render(jinja_dict=jinja_dict))
