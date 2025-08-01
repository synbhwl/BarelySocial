from pydantic import BaseModel

# These are pydantic models that parse the request body and
# puts the matching data in the object fields


class User_create(BaseModel):
    username: str
    password: str


class Message_create(BaseModel):
    receiver: str
    content: str
