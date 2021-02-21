import pandas as pd
import os


def run_each_repo(username, token, reponame, save_csv=True):
    if save_csv:
        os.system(f'gts {username}:{token} {reponame}')
    else:
        os.system(f'gts {username}:{token} {reponame} no_csv')


def run_all_repos(username, token, csv_file, save_csv=True):
    df = pd.read_csv(csv_file)
    # Exclude forks
    new_df = df.loc[df['fork'] == False]

    for reponame in new_df['name']:
        run_each_repo(username, token, reponame, save_csv=save_csv)
