from fastapi import FastAPI, Request, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import SQLModel, Field, Session, create_engine, select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import sqlite3
from passlib.hash import pbkdf2_sha256
import jwt
import json
from core.config import settings

#local imports
from models import User, Message
from core.database import create_session
from core.security import get_current_user

app = FastAPI()
secret = settings.JWT_SECRET
algo = "HS256"

# token = OAuth2PasswordBearer(tokenUrl = "login")

# def get_current_user(
#     req: Request, 
#     token: str = Depends(token),
#     session: Session = Depends(create_session)
#     ):

#     try:
#         payload = jwt.decode(token, secret, algorithms=[algo])
#     except Exception as e:
#         raise HTTPException(status_code=401, detail="couldnt get current user")
#     username = payload["username"]
#     if username == None:
#         raise HTTPException(status_code=400, deatil="No username in payload")

#     current_user = session.exec(select(User).where(User.username == username)).first()
#     if current_user == None:
#         raise HTTPException(status_code=404, deatil="username not found in database")
#     return current_user




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

#seeing list of chats
@app.get('/messages')
async def see_all_chats(
    session: Session = Depends(create_session),
    user: User = Depends(get_current_user)
    ):

    chats_raw = session.exec(select(Message).where((Message.receiver_id == user.id) | (Message.sender_id == user.id))).all()
    chat_list = set()
    for chat in chats_raw:
        if chat.sender_id == user.id:
            other_user_id = chat.receiver_id
        elif chat.receiver_id == user.id:
            other_user_id = chat.sender_id

        other_user = session.get(User, other_user_id)
        if other_user:
            chat_list.add(other_user.username)

    if not chat_list:
        return {"message":"you have no messages yet"}

    return Response(content=json.dumps(list(chat_list), indent=4), media_type='application/json')

#seeing the spcific chat of a username
@app.get('/messages/{username}')
async def see_specific_chat(
    username: str,
    session: Session = Depends(create_session),
    user: User = Depends(get_current_user)
    ):

    other_user = session.exec(select(User).where(User.username == username)).first()
    if other_user is None:
        return {'message':'user not found in database'}

    chat_full = []
    messages_raw = session.exec(
        select(Message).where(
           ((Message.sender_id == user.id) & (Message.receiver_id == other_user.id)) | ((Message.receiver_id == user.id) & (Message.sender_id == other_user.id))
        )).all()

    if not messages_raw:
        return {"message":"you have no chats with the user in the database"}

    for message in messages_raw:
        user_for_label = session.get(User, message.sender_id)
        chat_full.append({
            f"{user_for_label.username}":f"{message.content}",
            "timestamp":message.timestamp.isoformat()
        })

    if not chat_full:
        return {"message":"you have no chats with the user"}
    chat_full.sort(key=lambda x:x["timestamp"])

    final_chat = []
    for elements in chat_full:
        actual_msg = list(elements.items())[0]
        final_chat.append(dict([actual_msg]))

    return Response(content=json.dumps(final_chat, indent=4), media_type='application/json')

