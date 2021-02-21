import pandas as pd
import os


def run_each_repo(username, token, reponame):
    os.system(f'gts {username}:{token} {reponame}')


def run_all_repos(username, token, csv_file):
    df = pd.read_csv(csv_file)
    # Exclude forks
    new_df = df.loc[df['fork'] == False]

    for reponame in new_df['name']:
        run_each_repo(username, token, reponame)
