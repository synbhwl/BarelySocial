
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from passlib.hash import pbkdf2_sha256
import jwt

# local imports
from models import User
from core.database import create_session
from models.schemas.schemas import User_create
from core.config import settings  # noqa

secret = settings.JWT_SECRET
algo = "HS256"

router = APIRouter()

# route to greet


@router.get("/")
async def greet():
    return """hey there! welcome to BarelySocial.
    We are a backend-only minimal chat app.
    Consider register/logging in if you still haven't :)"""

# register_user regsiters the user and puts them
# into the database table for users


@router.post("/register")
async def register_user(
    user: User_create,
    session: Session = Depends(create_session)
):

    hashed = pbkdf2_sha256.hash(user.password)
    new_user = User(username=user.username, password=hashed)
    try:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return {"message": "user registered successfully"}
    except Exception as e:
        return {"error while registering": str(e)}

# login_user matches the username with database,
# matches the hashed password, logs in if matched, signs a jwt token and
# sends it to the client


@router.post("/login")
async def login_user(
    user: User_create,
    session: Session = Depends(create_session)
):
    try:
        statement = select(User).where(User.username == user.username)
        result = session.exec(statement)
        user_in_db = result.first()
        if user_in_db is None:
            return {"login_error": "username doesnt exist"}

        hashed_pass = user_in_db.password

        matched = pbkdf2_sha256.verify(user.password, hashed_pass)
        if matched is True:
            payload = {
                "username": user.username
            }
            token = jwt.encode(payload, secret, algorithm=algo)
            return {"message": "user logged in successfully", "token": token}
        else:
            return {"login_error": "wrong password"}
    except Exception as e:
        return {"error while logging in": str(e)}
