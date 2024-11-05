# src/main.py

from fastapi import FastAPI
from src.database import engine
from src.models import Base
from src.routers import spotify
from contextlib import asynccontextmanager
from src.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db() # 앱 시작 시 데이터베이스 초기화
    yield  # 종료 시에 수행할 추가 작업이 있다면 yield 이후에 추가 가능

app = FastAPI(lifespan=lifespan)

app.include_router(spotify.router, prefix="/spotify", tags=["Spotify"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Daily Jam!"}