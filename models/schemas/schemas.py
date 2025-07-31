from pydantic import BaseModel

# making a user class to hold the user objects with the two fields


class User_create(BaseModel):
    username: str
    password: str

# making a messages class to take messages


class Message_create(BaseModel):
    receiver: str
    content: str
