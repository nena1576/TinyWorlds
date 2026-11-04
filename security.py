# Everything security-related lives here:
#   1) password hashing (bcrypt)
#   2) JWT creation
#   3) get_current_user -> the dependency that protects routes
import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from config.db import get_db
from schemas.art_model import User

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY is not set. Create a .env file (copy .env.example) and set it with:\n"
        "    python -c \"import secrets; print(secrets.token_hex(32))\""
    )
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# tokenUrl must match the login route (auth router prefix + /token).
# This is also what makes the "Authorize" button work in /docs.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


# ---------------------- Password hashing ----------------------
def hash_password(password: str) -> str:
    """Hash with bcrypt. A random salt is generated and stored inside the hash."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:  # malformed hash or >72 byte password
        return False


# Used so a login for a non-existing user takes as long as a real one
# (prevents attackers from discovering which usernames exist by timing).
_DUMMY_HASH = hash_password("not-a-real-password")


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        verify_password(password, _DUMMY_HASH)
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# ---------------------- JWT ----------------------
def create_access_token(user: User, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": user.id, "username": user.username, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:  # bad signature, expired, malformed...
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Use on routes only the site owner may call. Role is read from the DB on every
    request (not from the token), so removing someone's admin role takes effect immediately."""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user
