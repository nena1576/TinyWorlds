# Register + login endpoints.
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from config.db import get_db
from schemas.art_model import User
from schemas.schemas import UserCreate, UserOut, Token
from security import hash_password, authenticate_user, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    email = user_data.email.lower()
    exists = db.query(User).filter((User.username == user_data.username) | (User.email == email)).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email already registered")

    user = User(
        id=str(uuid4()),
        username=user_data.username,
        email=email,
        hashed_password=hash_password(user_data.password),  # <- the hashing step
        created_at=datetime.now(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# OAuth2PasswordRequestForm expects FORM data (fields: username, password), not JSON.
@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_access_token(user), "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user
