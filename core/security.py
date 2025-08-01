from fastapi import Request, Depends, HTTPException
import jwt
from fastapi.security import OAuth2PasswordBearer
from core.database import create_session
from core.config import settings
from sqlmodel import Session, select
from models import User

secret = settings.JWT_SECRET
algo = "HS256"

# this parses the token from the auth header
# since the jwt is encoded in the login route,
# that's where it gets the token from

token = OAuth2PasswordBearer(tokenUrl="login")

# get_current_user is a substitute for auth middleware and req.state.user
# that we would have had to manually set inside the auth middleware


def get_current_user(
    req: Request,
    token: str = Depends(token),
    session: Session = Depends(create_session)
):

    try:
        payload = jwt.decode(token, secret, algorithms=[algo])
    except Exception:
        raise HTTPException(status_code=401, detail="invalid token")
    username = payload["username"]
    if username is None:
        raise HTTPException(status_code=400, detail="No username in payload")

    current_user = session.exec(select(User).where(
        User.username == username)).first()
    if current_user is None:
        raise HTTPException(
            status_code=404, deatil="no such username exists")
    return current_user
