# These are the Pydantic models — they define what data we accept/return
# through the API (like a form with required fields), and they're what
# validates incoming requests before anything touches the database.
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import uuid4
#this is the CRUD model for the art table, it defines the structure of the data we will be working with in our API.
class ArtCreate(BaseModel):
    title: str
    description: str
    author: str
# C stands for Create
class ArtUpdate(BaseModel):
    title: str
    description: str
    author: str
#U stands for Update
class Art(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: str
    author: str
    created_at: datetime = Field(default_factory=datetime.now)
    published_at: Optional[datetime] = None
    published: bool = False
#This is the main Art model that represents the structure of the data in the database. It includes all fields, including the ID and timestamps.

# ---------------------- Users / Auth ----------------------
from pydantic import EmailStr, ConfigDict, field_validator


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, v: str) -> str:
        # bcrypt only supports up to 72 BYTES (not characters).
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 bytes long")
        return v


# What we send BACK to the client. Note: no password / hash field at all.
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    username: str
    email: EmailStr
    role: str
    created_at: datetime


class ChatMessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=500)

    @field_validator("content")
    @classmethod
    def not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Message cannot be empty")
        return v


class ChatMessageOut(BaseModel):
    id: int
    username: str
    content: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str
