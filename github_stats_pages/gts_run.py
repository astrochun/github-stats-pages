import os


def run_each_repo(username, token, reponame, save_csv=True):
    if save_csv:
        os.system(f'gts {username}:{token} {reponame}')
    else:
        os.system(f'gts {username}:{token} {reponame} no_csv')
