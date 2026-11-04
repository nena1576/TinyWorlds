# This is the entry point of the app. It creates the FastAPI instance
# and plugs in all our routes so the app actually knows about them.
from fastapi import FastAPI, status, Depends
from sqlalchemy.orm import Session

from schemas import art_model          # importing registers the tables
from config.db import engine, meta, Base, get_db
from routers.routers import router
from routers.auth import router as auth_router
from routers.chat import router as chat_router

# Create tables (art uses `meta`, users uses `Base`)
meta.create_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TinyWorlds")
app.include_router(auth_router)
app.include_router(router)
app.include_router(chat_router)


@app.get("/", status_code=status.HTTP_200_OK)
async def user(db: Session = Depends(get_db)):
    return {"message": "Welcome to TinyWorlds!"}
