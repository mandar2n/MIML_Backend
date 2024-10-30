# src/routers/spotify.py

from fastapi import APIRouter, HTTPException, Query
from src.services.spotify_service import get_song_info  # src 경로로 import 수정

router = APIRouter()

@router.get("/search")
def search_song(song_name: str = Query(..., description="Name of the song to search")):
    """
    노래를 검색하기 위한 엔드포인트. 검색된 모든 노래의 목록을 반환합니다.
    """
    songs = get_song_info(song_name)
    if not songs:
        raise HTTPException(status_code=404, detail="No songs found with the given name")
    return {"songs": songs}