# This defines what our tables look like in the database.
# Think of this as the database-side blueprint: columns, types, etc.
from sqlalchemy import Table, Column, String, DateTime, Boolean, Integer, ForeignKey
from config.db import meta, Base

art = Table("art", meta,
    Column("id", String(36), primary_key=True),
    Column("title", String(255)),
    Column("description", String(1000)),
    Column("author", String(255)),
    Column("created_at", DateTime),
    Column("published_at", DateTime, nullable=True),
    Column("published", Boolean, default=False))


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    # NEVER the plain password. This stores the bcrypt hash (~60 chars).
    hashed_password = Column(String(255), nullable=False)
    # "user" (default, can use the chat) or "admin" (can also edit the art catalog).
    # Nobody can become admin through the API; see make_admin.py
    role = Column(String(20), nullable=False, default="user", server_default="user")
    created_at = Column(DateTime, nullable=False)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(String(500), nullable=False)
    created_at = Column(DateTime, nullable=False, index=True)

# NOTE: the tables are created in main.py (Base.metadata.create_all + meta.create_all)
