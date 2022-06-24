from typing import Optional

from sqlmodel import SQLModel, Field


class Paths(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: str
    repository_name: Optional[str]
    path: str
    title: str
    views: int
    unique_views: int
