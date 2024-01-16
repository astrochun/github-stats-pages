from pathlib import Path

from github_stats_pages import db

t_data = Path("tests_data/data/")


def test_migrate_csv(test_engine):
    # This CSV is already present so no new records exist
    db.migrate_csv(t_data / "merged_clone.csv", db.Clone, test_engine)

    # This will add new records and ensure Paths testing
    db.migrate_csv(t_data / "merged_paths.csv", db.Paths, test_engine)


def test_query(test_engine):

    t_query = db.query(
        "github-stats-pages", "2021-02-28", test_engine, db.Clone
    )
    assert isinstance(t_query, db.Clone)

    t_query = db.query(
        "github-stats-pages", "2021-02-28", test_engine, db.Traffic
    )
    assert isinstance(t_query, db.Traffic)

    # This returns a None result
    assert not db.query(
        "github-stats-pages", "2020-01-01", test_engine, db.Clone
    )


def test_query_all(test_engine):

    t_query = db.query_all(test_engine, db.Clone)
    assert isinstance(t_query, list)
