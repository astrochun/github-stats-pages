#!/bin/bash
# Usage:
# $ bash ./scripts/merge-csv.sh [directory_with_csv_files]
# Based on nchah's script but modified to separate out the different types

d_dir="data"  # Data directory for all CSV files

if [[ -z $1 ]]; then wd='.'; else wd=$1; fi

for stat_type in traffic clone referrer
do
    # Merge all non-header lines into merged.csv
    for fname in ${wd}/${d_dir}/*${stat_type}-stats.csv
    do
      tail -n+2 $fname >> ${wd}/${d_dir}/merged.csv
    done

    # Get the unique rows by column 1, 2
    awk -F"," '!seen[$1, $2]++' ${wd}/${d_dir}/merged.csv > ${wd}/${d_dir}/merged2.csv

    # Sort the final rows in alpha order - first by the first col., then by second col.
    sort -k1,1 -k2,2 ${wd}/${d_dir}/merged2.csv > ${wd}/${d_dir}/merged_${stat_type}.csv

    # Rename and cleanup output
    rm ${wd}/${d_dir}/merged.csv
    rm ${wd}/${d_dir}/merged2.csv
done
