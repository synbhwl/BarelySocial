from fastapi import Request, Depends, HTTPException, status
import jwt
from fastapi.security import OAuth2PasswordBearer
from core.database import create_session
from core.config import settings
from sqlmodel import Session, select
from models import User

secret = settings.JWT_SECRET
algo = "HS256"

token = OAuth2PasswordBearer(tokenUrl = "login")

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
