from typing import Optional

from sqlmodel import SQLModel, Field


class Traffic(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    repository_name: str
    date: str
    views: int
    unique_visitors: int
