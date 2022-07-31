__version__ = "0.4.14"

RENAME_MAPPING = {
    "count": "views",  # for paths
    "unique_visitors/cloners": "unique",  # for clones, traffic, referrer
    "uniques": "unique",  # for paths
}

STATS_TYPES = ["clone", "paths", "referrer", "traffic"]

STATS_COLUMNS = {
    "clone": ["repository_name", "date", "clones", "unique"],
    "paths": ["repository_name", "date", "path", "title", "views", "unique"],
    "referrer": ["repository_name", "date", "site", "views", "unique"],
    "traffic": ["repository_name", "date", "views", "unique"],
}

STATS_SORT_DATAFRAME = {
    "clone": ["repository_name", "date"],
    "paths": ["repository_name", "date", "path"],
    "referrer": ["repository_name", "date", "site"],
    "traffic": ["repository_name", "date"],
}
