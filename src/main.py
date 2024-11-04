# src/main.py

from fastapi import FastAPI
from src.database import engine
from src.models import Base
from src.routers import spotify
app = FastAPI()
app.include_router(spotify.router, prefix="/spotify", tags=["Spotify"])
# 데이터베이스 생성
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to Daily Jam!"}