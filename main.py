from fastapi import FastAPI
from routes import auth_routes, message_routes

app = FastAPI()

app.include_router(auth_routes.router)
app.include_router(message_routes.router)
