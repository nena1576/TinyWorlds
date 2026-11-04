# Community chat. Any logged-in user can read and post; only admin can delete messages.
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from config.db import get_db
from schemas.art_model import ChatMessage, User
from schemas.schemas import ChatMessageCreate, ChatMessageOut
import database
from security import get_current_user, require_admin

router = APIRouter(prefix="/chat", tags=["chat"])


def _out(msg: ChatMessage, username: str) -> dict:
    return {"id": msg.id, "username": username, "content": msg.content, "created_at": msg.created_at}


@router.get("", response_model=list[ChatMessageOut])
def list_messages(
    limit: int = Query(50, ge=1, le=100),
    before_id: Optional[int] = Query(None, description="Load older messages (scroll up)"),
    after_id: Optional[int] = Query(None, description="Load only newer messages (polling)"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(ChatMessage, User.username).join(User, User.id == ChatMessage.user_id)
    if after_id is not None:
        rows = q.filter(ChatMessage.id > after_id).order_by(ChatMessage.id.asc()).limit(limit).all()
    else:
        if before_id is not None:
            q = q.filter(ChatMessage.id < before_id)
        rows = list(reversed(q.order_by(ChatMessage.id.desc()).limit(limit).all()))  # oldest -> newest
    return [_out(m, name) for m, name in rows]

@router.get("/export", dependencies=[Depends(require_admin)])
def export_chat(db: Session = Depends(get_db)):
    filepath, count = database.export_chat_to_json(db)
    return {"message": f"Exported {count} messages to {filepath}"}

@router.post("", response_model=ChatMessageOut, status_code=status.HTTP_201_CREATED)
def post_message(data: ChatMessageCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    msg = ChatMessage(user_id=user.id, content=data.content, created_at=datetime.now())
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return _out(msg, user.username)


@router.delete("/{message_id}", dependencies=[Depends(require_admin)])
def delete_message(message_id: int, db: Session = Depends(get_db)):
    msg = db.get(ChatMessage, message_id)
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    db.delete(msg)
    db.commit()
    return {"message": "Message deleted"}
