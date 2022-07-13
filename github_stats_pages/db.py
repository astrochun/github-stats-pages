from functools import partial
from pathlib import Path
from typing import List, Type, Union

import pandas as pd
from sqlalchemy.future import Engine
from sqlalchemy.exc import NoResultFound
from sqlmodel import SQLModel, Session, create_engine, select

from .models import Clone, Referring, Traffic, Paths
from .logger import app_log as log

SQLITE_FILE_NAME = Path("data/sqlite3.db")


def configure(test: bool = False, echo: bool = False) -> Engine:
    sqlite_file_name = (
        Path("tests_data/sqlite3.db") if test else SQLITE_FILE_NAME
    )
    if not sqlite_file_name.parent.exists():  # pragma: no cover
        sqlite_file_name.parent.mkdir()
    sqlite_url = f"sqlite:///{sqlite_file_name}"
    log.info(f"Configuring SQLite at: {sqlite_url}")
    return create_engine(sqlite_url, echo=echo)


def create_db_and_tables(test: bool = False, echo: bool = False):
    engine = configure(test=test, echo=echo)
    SQLModel.metadata.create_all(engine)
    return engine


def migrate_csv(
    filename: Union[str, Path],
    model: Type[SQLModel],
    engine: Engine,
    skip_rows: Union[int, None] = None,
):
    """Migrate CSV over to SQLite"""

    names = list(
        map(
            lambda f: f.name,
            filter(lambda x: x.required, model.__fields__.values()),
        )
    )
    log.info(f"[yellow]Loading: {filename}")
    df = pd.read_csv(filename, header=None, skiprows=skip_rows, names=names)
    log.info(f"Size of dataframe: {len(df)}")
    if model.__name__ == "Paths":
        repository_names = [a.split("/")[2] for a in df["path"].values]
        df.insert(1, "repository_name", repository_names)

    if model.__name__ == "Paths":
        func = partial(query_path, engine=engine, model=model)
        query_results = list(
            map(func, df["repository_name"], df["date"], df["path"])
        )
    else:
        func = partial(query, engine=engine, model=model)
        query_results = list(map(func, df["repository_name"], df["date"]))

    new_df: pd.DataFrame = df.iloc[
        [idx for idx, item in enumerate(query_results) if not item]
    ]
    if new_df.empty:
        log.info("No new records!")
    else:
        log.info(f"New records found: {len(new_df)}")
        log.info("[bold yellow]Adding data")
        new_df.to_sql(
            model.__name__.lower(), engine, if_exists="append", index=False
        )
        if len(new_df) < len(df):  # pragma: no cover
            log.info("[orange]Some records exists in db")


def query(
    repository_name: str,
    date: str,
    engine: Engine,
    model: Union[Type[SQLModel], Clone, Referring, Paths, Traffic],
) -> Union[SQLModel, Clone, Referring, Paths, Traffic, None]:

    with Session(engine) as session:
        result = session.exec(
            select(model).where(
                model.repository_name == repository_name, model.date == date
            )
        )
        try:
            return result.one()
        except NoResultFound:
            return


def query_all(
    engine: Engine,
    model: Union[Type[SQLModel], Clone, Referring, Paths, Traffic],
) -> List[Union[SQLModel, Clone, Referring, Paths, Traffic]]:
    """Retrieve an entire table"""

    with Session(engine) as session:
        result = session.exec(select(model))
        return result.all()


def query_path(
    repository_name: str,
    date: str,
    path: str,
    engine: Engine,
    model: Union[Type[SQLModel], Paths],
) -> Union[SQLModel, Paths, None]:

    with Session(engine) as session:
        result = session.exec(
            select(model).where(
                model.repository_name == repository_name,
                model.date == date,
                model.path == path,
            )
        )
        try:
            return result.one()
        except NoResultFound:
            return
