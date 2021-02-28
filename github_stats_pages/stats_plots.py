from pathlib import Path
from typing import Dict

import pandas as pd
from datetime import datetime as dt, timedelta as td

# Bokeh Libraries
from bokeh.io import output_file
from bokeh.plotting import figure, save
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, VBar  # HoverTool

prefix = 'merged'
stats_type = ['traffic', 'clone', 'referrer']
columns = ['repository_name', 'date', 'total', 'unique']

TOOLTIPS = [
    ("index", "$index"),
    ("(x,y)", "($x, $top)"),
]


def load_data(data_dir: str) -> Dict[str, pd.DataFrame]:
    """
    Load stats CSV as dict of pandas DataFrame

    :param data_dir: Path containing merged*.csv
    :return: Dict of pandas DataFrame
    """
    p = Path(data_dir)

    dict_df = {}

    for stats in stats_type:
        stat_file = p / f'{prefix}_{stats}.csv'
        dict_df[stats] = pd.read_csv(stat_file, header=None, names=columns)

    return dict_df


def subplots(df: pd.DataFrame, y_column: str, title: str = '',
             pw: int = 350, ph: int = 350, bc: str = "#fafafa") -> figure():

    s = figure(plot_width=pw, plot_height=ph, background_fill_color=bc,
               x_axis_type="datetime", title=title, tooltips=TOOLTIPS,
               tools="pan,box_zoom,wheel_zoom,hover,save,reset")
    # s.toolbar.active_inspect = [HoverTool()]

    s.axis.major_tick_in = 6
    s.axis.major_tick_out = 0
    s.axis.minor_tick_in = 3
    s.axis.minor_tick_out = 0

    x = [dt.strptime(d, '%Y-%m-%d') for d in df['date']]
    y = df[y_column]
    g_source = ColumnDataSource(data={'x': x, 'top': y})
    glyphs = VBar(x='x', top='top', bottom=0, width=td(days=1),
                  fill_color="#6fa1f8", fill_alpha=0.5, line_color=None)
    s.add_glyph(g_source, glyphs)
    # s.vbar(x=x, top=y, width=5.0)
    s.xaxis.formatter = DatetimeTickFormatter(years=["%Y %m"])

    return s


def make_plots(data_dir: str, out_file: str):

    dict_df = load_data(data_dir)

    # Get unique repository names
    repo_names = set()
    for key, df in dict_df.items():
        repo_names.update(set(df[columns[0]].unique()))

    n_repo_names = len(repo_names)
    print(f"Number of GitHub repositories: {n_repo_names}")

    traffic_df = dict_df['traffic']
    clone_df = dict_df['clone']
    referrer_df = dict_df['referrer']

    pw = 350  # plot width
    ph = 350  # plot height
    bc = "#fafafa"  # background color

    for r in ['Metallicity_Stack_Commons']:
        output_file(out_file, title=f'GitHub Traffic Stats : {r}')

        r_traffic_df = traffic_df.loc[traffic_df[columns[0]] == r]
        r_clone_df = clone_df.loc[clone_df[columns[0]] == r]
        # r_referrer_df = referrer_df.loc[referrer_df[columns[0]] == r]

        # Plot traffic data
        s1a = subplots(r_traffic_df, 'total', 'Total Daily Traffic', pw=pw,
                       ph=ph, bc=bc)

        s1b = subplots(r_traffic_df, 'unique', 'Unique Daily Traffic', pw=pw,
                       ph=ph, bc=bc)

        # Plot clones traffic
        s2a = subplots(r_clone_df, 'total', 'Total Daily Clones', pw=pw,
                       ph=ph, bc=bc)

        s2b = subplots(r_clone_df, 'unique', 'Unique Daily Clones', pw=pw,
                       ph=ph, bc=bc)

        grid = gridplot([[s1a, s1b], [s2a, s2b]], plot_width=pw, plot_height=ph)

        save(grid)
