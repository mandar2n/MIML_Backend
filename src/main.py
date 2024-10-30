# src/main.py

from fastapi import FastAPI
from src.routers import spotify  # src/routers/spotify.py에서 import

app = FastAPI()

# Spotify 라우터 포함
app.include_router(spotify.router, prefix="/spotify", tags=["Spotify"])

# 기본 루트 엔드포인트
@app.get("/")
def read_root():
    return {"message": "Welcome to the Daily Jam Spotify API"}