from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import SQLModel, Field, Session, create_engine, select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import sqlite3
from passlib.hash import pbkdf2_sha256
import jwt
from core.config import settings

app = FastAPI()
secret = settings.JWT_SECRET
algo = "HS256"
# EXCLUDE = ['/','/register','/login', '/docs', '/openapi.json']

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username:str
    password: str

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sender_id: int 
    receiver_id: int
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

engine = create_engine("sqlite:///data.db")
SQLModel.metadata.create_all(engine)

def create_session():
    with Session(engine) as session:
        yield session

token = OAuth2PasswordBearer(tokenUrl = "login")
# auth middleware that verifies the auth header bearer token
# @app.middleware('http')
def get_current_user(
    req: Request, 
    token: str = Depends(token),
    session: Session = Depends(create_session)
    ):

    try:
        payload = jwt.decode(token, secret, algorithms=[algo])
    except Exception as e:
        raise HTTPException(status_code=401, detail="couldnt get current user")
    username = payload["username"]
    if username == None:
        raise HTTPException(status_code=400, deatil="No username in payload")

    current_user = session.exec(select(User).where(User.username == username)).first()
    if current_user == None:
        raise HTTPException(status_code=404, deatil="username not found in database")
    return current_user




# making a user class to hold the user objects with the two fields
class User_create(BaseModel):
    username : str
    password : str

# making a messages class to take messages 
class Message_create(BaseModel):
    receiver : str
    content : str

# greet greets the user when they land at the root route or basic url of the server
@app.get("/")
async def greet():
    return "hey there! welcome to BarelySocial. We are a backend-only minimal chat app. Consider register/logging in if you still haven't :)"

# register_user regsiters the user and puts them into the database table for users
@app.post("/register")
async def register_user(user: User_create, session: Session= Depends(create_session)):
    hashed = pbkdf2_sha256.hash(user.password)
    new_user = User(username=user.username, password=hashed)
    try:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return {"message":"user registered successfully"}
    except Exception as e:
        return {"error while registering": str(e)}

# login_user matches the username with database, matches the hashed password, logs in if matched, signs a jwt token and sends it to the client
@app.post("/login")
async def login_user(user: User_create, session: Session = Depends(create_session)):
    try:
        statement = select(User).where(User.username == user.username)
        result = session.exec(statement)
        user_in_db = result.first()
        if user_in_db is None:
            return {"login_error":"username doesnt exist"}

        hashed_pass = user_in_db.password

        matched = pbkdf2_sha256.verify(user.password, hashed_pass)
        if matched == True:
            payload = {
                "username":user.username
            }
            token = jwt.encode(payload, secret, algorithm=algo)
            return {"message":"user logged in successfully", "token":token}
        else :
            return {"login_error": "wrong password"}
    except Exception as e:
        return {"error while logging in": str(e)}

#sending messages 
@app.post('/messages/new')
async def send_message(
    req: Request, 
    message: Message_create, 
    session: Session = Depends(create_session),
    user: User = Depends(get_current_user)
    ):

    sender_id = user.id

    receiver_in_db = session.exec(select(User).where(User.username == message.receiver)).first()
    if receiver_in_db == None:
        raise HTTPException(status_code=404, detail="receiver not found in database")
    receiver_id = receiver_in_db.id

    new_message = Message(sender_id=sender_id, receiver_id=receiver_id, content=message.content)

    session.add(new_message)
    session.commit()
    session.refresh(new_message)

    return {"message":f"message was sent to {message.receiver} as {new_message.content}"}