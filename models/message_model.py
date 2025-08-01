
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

# this is the database table that holds all the messages


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sender_id: int
    receiver_id: int
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
