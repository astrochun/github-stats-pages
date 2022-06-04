from typing import Optional

from sqlmodel import SQLModel, Field


class Referring(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    repository_name: str
    site: str
    date: str
    views: int
    unique_visitors: int
