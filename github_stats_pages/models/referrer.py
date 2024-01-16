from typing import Optional

from sqlmodel import SQLModel, Field


class Referrer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    repository_name: str
    site: str
    date: Optional[str]
    views: int
    unique: int
