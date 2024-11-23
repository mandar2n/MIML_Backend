# src/routers/spotify.py
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.spotify_service import get_song_info, get_song_details
from src.database import get_db
from src.crud import share_song
from src.schemas import SongShare, SongDetailResponse
from src.models import User

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

