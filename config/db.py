
# This file sets up the database connection and manages ORM sessions.
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Load environment variables from the local .env file, if it exists.
load_dotenv()

# DATABASE_URL comes from the environment so credentials stay out of the code.
# Locally, set DATABASE_URL in .env to your MySQL connection string.
# On the hosting service, configure DATABASE_URL in its environment settings.
DATABASE_URL = os.getenv("DATABASE_URL")

# Stop early with a clear error if the database URL has not been configured.
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is missing. Configure it in your .env file or server settings."
    )

# The engine manages connections between SQLAlchemy and the database.
engine = create_engine(DATABASE_URL)

# This metadata collection tracks the art table defined with SQLAlchemy Core.
meta = MetaData()


# Base is the common parent for ORM models such as User and ChatMessage.
class Base(DeclarativeBase):
    pass


# SessionLocal creates a separate database session when a request needs one.
SessionLocal = sessionmaker(bind=engine)


# FastAPI uses this dependency to provide a session and close it after the request.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

