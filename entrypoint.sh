#!/bin/bash

# To activate testing for quick run / CI
if [ -z $3 ]; then
  test=""
else
  test="--test"
fi

# For include_repo flag
if [ -z $4 ]; then
  include_repo=''
else
  include_repo="--include-repo $4"
fi

# For exclude_repo flag
if [ -z $5 ]; then
  exclude_repo=''
else
  exclude_repo="--exclude-repo $5"
fi

get_repo_list -u $1
gts_run_all_repos -u $1 -t $2 -c "$1".csv ${test}
merge-csv.sh .
make_stats_plots -u $1 -t $2 -c "$1".csv ${include_repo} ${exclude_repo}
