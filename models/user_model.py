
from sqlmodel import SQLModel, Field
from typing import Optional

# this is the database table that holds all the users


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str
