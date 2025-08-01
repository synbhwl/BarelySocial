```
BarelySocial
============

BarelySocial is a backend-only messaging API built with FastAPI and SQLModel

It supports registration, login (with JWT), sending and viewing messages between users. 

URL - https://barelysocial-production.up.railway.app

Features
========
- auth using JWT
- sending and viewing messages
- viewing chat list 
- RESTful Endpoints
- SQLite(dev)/ PostgresSQL(prod)

Tech stack
==========
- FastAPI
- SQLModel
- Uvicorn
- pyJWT
- PostgreSQL (via Railway)
- pydantic 
- passlib

for full dependency list, check requirements.txt in the repo

Installation (Local)
====================

In Bash
-------
git clone https://github.com/synbhwl/BarelySocial.git
cd BarelySocial
pip install -r requirements.txt

create a .env file
------------------
JWT_SECRET=your_secret_here
DATABASE_URL=sqlite://data.db

In Bash run
-----------
uvicorn main:app --reload

API Endpoints
=============

Auth
----
- POST /register - register a new user
- POST /login - login and recieve JWT token

Messages (JWT required)
--------
- POST /messages/new - send a message to a user by username
- GET /messages - list all chats (usernames you have talked to)
- GET /messages/{username} - view chat with a user

How to use 
==========

Note: Due to simplified JWT handling, Swagger UI (https://barelysocial-production.up.railway.app/docs) only supports greeting, registration and login in this setup. However, every route is supported if you are using any HTTP client (like cURL, Postman etc)

cURL command boilerplates
-------------------------
For greeting -

curl https://barelysocial-production.up.railway.app

For registering a new user -

curl -k -X POST https://barelysocial-production.up.railway.app/register \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"username":"example", "password":"example@123"}'

For logging in -

curl -k -X POST https://barelysocial-production.up.railway.app/login \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"username":"example", "password":"example@123"}'

Note: You'll get a token after logging in successfully, copy the token and put it in a safe private place. We'll need it for all the following protected routes. Do not share it with anyone.

For sending a message -

curl -k -X POST https://barelysocial-production.up.railway.app/messages/new \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token-here" \
  -d '{"receiver": "example", "content": "your example message"}'

For viewing the chat list -

curl -k -X GET https://barelysocial-production.up.railway.app/messages \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token-here"

For viewing your chat with a user -

curl -k -X GET https://barelysocial-production.up.railway.app/messages/example_username \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token-here"

Mobile use
----------

If you want to test it on your phone, download an HTTP client. I use ApiClient:REST API Client by Abcoderz Software.

To send a request, select the method in the left of the URL bar, paste the full URL (with the endpoint) in the URL bar, write a header where key is 'Authorization' and value is the token you got. Then, write the request Body (if required any) in the textbox below in this format '{"username":"example", "password":"example@123"}'

if you want to send me messages :)
===============================
my username is synbhwl

```