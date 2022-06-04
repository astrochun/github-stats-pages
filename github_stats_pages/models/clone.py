from typing import Optional

from sqlmodel import SQLModel, Field


class Clone(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    repository_name: str
    date: str
    clones: int
    unique_clones: int
