# src/main.py

from fastapi import FastAPI
from src.database import engine
from src.models import Base
from src.routers import spotify, songs, users,feed
from contextlib import asynccontextmanager
from src.database import init_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db() # 앱 시작 시 데이터베이스 초기화
    yield  # 종료 시에 수행할 추가 작업이 있다면 yield 이후에 추가 가능

app = FastAPI(lifespan=lifespan)
# 각각의 라우터를 앱에 추가

app.include_router(spotify.router, prefix="/spotify", tags=["Spotify"])
app.include_router(songs.router, prefix="/songs", tags=["Songs"])
app.include_router(users.router, prefix="/users", tags=["Users"])  # users 라우터 추가
app.include_router(feed.router, prefix="/feed", tags=["Feed"])
# app.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
# app.include_router(playlists.router, prefix="/playlists", tags=["Playlists"])
# app.include_router(charts.router, prefix="/charts", tags=["Charts"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Daily Jam!"}