from fastapi import FastAPI, Request
from pydantic import BaseModel
import sqlite3
from passlib.hash import pbkdf2_sha256
import os
from dotenv import load_dotenv
import jwt

app = FastAPI()
load_dotenv()
secret = os.getenv("JWT_SECRET")
algo = "HS256"
EXCLUDE = ['/','/register','/login', '/docs', '/openapi.json']

# auth middleware that verifies the auth header bearer token
@app.middleware('http')
async def authmw(req: Request, call_next) :
    path = req.url.path
    if path in EXCLUDE:
        return await call_next(req)
    
    header= req.headers.get('authorization')
    if not header or not header.startswith('Bearer'):
        return {"404 error":"missing auth header"}

    token = header.split(' ')[1]
    try:
        payload = jwt.decode(token, secret, algorithms=[algo])
        req.state.user = payload
    except jwt.InvalidTokenError as e:
        return {"token error":str(e)}

    return await call_next(req)


# opening the database file in a global context manager to create the initial table to hold users (id will be automatically incremented and this needn't be inserted manually)
with sqlite3.connect('data.db') as conn:
    conn.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        username TEXT NOT NULL UNIQUE,
        password NOT NULL
    );""")

# making a user class to hold the user objects with the two fields
class User(BaseModel):
    username : str
    password : str

# greet greets the user when they land at the root route or basic url of the server
@app.get("/")
async def greet():
    return "hey there! welcome to BarelySocial. We are a backend-only minimal chat app. Consider register/logging in if you still haven't :)"

# register_user regsiters the user and puts them into the database table for users
@app.post("/register")
async def register_user(user: User):
    try:
        hashed = pbkdf2_sha256.hash(user.password)
        with sqlite3.connect('data.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user.username, hashed))
            return {"message":"user registered successfully"}
    except sqlite3.IntegrityError as e:
        return {"error while registering": str(e)}

# login_user matches the username with database, matches the hashed password, logs in if matched, signs a jwt token and sends it to the client
@app.post("/login")
async def login_user(user: User):
    try:
        with sqlite3.connect('data.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE username = ?);", (user.username,))
            row_exists = cursor.fetchone()[0]
            if row_exists == 0:
                return {"error while logging in": "username doesnt exist"}

            cursor.execute("SELECT (password) FROM users WHERE username = ?", (user.username,))
            hashed_pass = cursor.fetchone()[0]

            matched = pbkdf2_sha256.verify(user.password, hashed_pass)
            if matched == True:
                payload = {
                    "username":user.username
                }
                token = jwt.encode(payload, secret, algorithm=algo)
                return {"message":"user logged in successfully", "token":token}
            else :
                return {"error while logging in": "wrong password"}
    except Exception as e:
        return {"error while logging in": str(e)}

# test protected 
@app.get('/protected')
async def something():
    return {"message":"you are now logged in"}