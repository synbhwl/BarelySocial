
from fastapi import APIRouter, Depends, HTTPException, status
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

# this is the landing route


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

    if (not user.username) or (not user.password):
        raise HTTPException(
            Status_code=status.HTTP_400_BAD_REQUEST,
            detail="username or password missing"
        )
    hashed = pbkdf2_sha256.hash(user.password)
    new_user = User(username=user.username, password=hashed)
    try:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return {"message": "user registered successfully"}
    except Exception:
        raise HTTPException(
            Status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Couldn't register user due to database issue"
        )

# login_user matches the username with database,
# matches the hashed password, logs in if matched, signs a jwt token and
# sends it to the client


@router.post("/login")
async def login_user(
    user: User_create,
    session: Session = Depends(create_session)
):
    if (not user.username) or (not user.password):
        raise HTTPException(
            Status_code=status.HTTP_400_BAD_REQUEST,
            detail="username or password missing"
        )
    try:
        user_in_db = session.exec(
            select(User).where(User.username == user.username)
        ).first()
        if user_in_db is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="no such username exists"
            )

        hashed_pass = user_in_db.password

        matched = pbkdf2_sha256.verify(user.password, hashed_pass)
        if matched is True:
            payload = {
                "username": user.username
            }
            token = jwt.encode(payload, secret, algorithm=algo)
            return {"message": "user logged in successfully", "token": token}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="credentials wrong"
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="couldn't login user"
        )
