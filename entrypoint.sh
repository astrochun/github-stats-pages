#!/bin/bash

# For include_repos flag
if [ -z $3 ]; then
  include_repos=''
else
  include_repos="--include-repos $3"
fi

# For exclude_repos flag
if [ -z $4 ]; then
  exclude_repos=''
else
  exclude_repos="--exclude-repos $4"
fi

# To activate testing for quick runs / CI
if [ -z $5 ]; then
  test=""
else
  test="--test"
fi

migrate_to_sqlite

get_repo_list -u $1

gts_run_all_repos -u $1 -t $2 -c "$1".csv ${test}
ret=$?
if [ $ret -ne 0 ]; then
  exit 1
fi

# merge-csv.sh .
make_stats_plots -u $1 -t $2 -c "$1".csv -o ./public ${include_repos} ${exclude_repos}
