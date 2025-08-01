# from fastapi import APIRouter

from fastapi import (
    APIRouter,
    Request,
    Depends,
    HTTPException,
    Response,
    status)
from sqlmodel import Session, select
import json

# local imports
from models import User, Message
from core.database import create_session
from core.security import get_current_user
from models.schemas.schemas import Message_create

router = APIRouter()

# sending messages


@router.post('/messages/new')
async def send_message(
    req: Request,
    message: Message_create,
    session: Session = Depends(create_session),
    user: User = Depends(get_current_user)
):

    if not message.receiver or not message.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="reciever or content missing"
        )
    sender_id = user.id

    receiver_in_db = session.exec(select(User).where(
        User.username == message.receiver)).first()
    if receiver_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="receiver not found in database"
        )
    receiver_id = receiver_in_db.id

    new_message = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=message.content
    )
    try:
        session.add(new_message)
        session.commit()
        session.refresh(new_message)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="something went wrong"
        )

    return {
        "message": f"""message was sent to
        {message.receiver} as {new_message.content}"""
    }

# seeing list of chats


@router.get('/messages')
async def see_all_chats(
    session: Session = Depends(create_session),
    user: User = Depends(get_current_user)
):

    chats_raw = session.exec(select(Message).where(
        (Message.receiver_id == user.id) |
        (Message.sender_id == user.id))).all()
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
        return {"message": "you have no messages yet"}

    return Response(
        content=json.dumps(list(chat_list), indent=4),
        media_type='application/json'
    )

# seeing the spcific chat of a username


@router.get('/messages/{username}')
async def see_specific_chat(
    username: str,
    session: Session = Depends(create_session),
    user: User = Depends(get_current_user)
):
    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="receiver username missing"
        )

    other_user = session.exec(select(User).where(
        User.username == username)).first()
    if other_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="no such username exists"
        )

    chat_full = []
    messages_raw = session.exec(
        select(Message).where(
            ((Message.sender_id == user.id) &
             (Message.receiver_id == other_user.id)) |
            ((Message.receiver_id == user.id) &
             (Message.sender_id == other_user.id))
        )).all()

    if not messages_raw:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="no messages found with the user"
        )

    for message in messages_raw:
        user_for_label = session.get(User, message.sender_id)
        chat_full.append({
            f"{user_for_label.username}": f"{message.content}",
            "timestamp": message.timestamp.isoformat()
        })

    chat_full.sort(key=lambda x: x["timestamp"])

    final_chat = []
    for elements in chat_full:
        actual_msg = list(elements.items())[0]
        final_chat.append(dict([actual_msg]))

    return Response(
        content=json.dumps(final_chat, indent=4),
        media_type='application/json'
    )
