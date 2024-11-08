# src/routers/songs.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.crud import share_song
from src.schemas import SongShare  # SongShare 스키마 추가 필요

router = APIRouter()

@router.post("/share")
async def share_song_to_feed(song: SongShare, db: Session = Depends(get_db)):
    """
    사용자가 노래를 선택하여 피드에 공유하는 엔드포인트
    """
    shared_song = await share_song(
        db=db,
        user_id=song.userId,
        song_title=song.title,
        artist=song.artist,
        album=song.album,
        spotify_url=song.spotify_url,   
        album_cover_url=song.album_cover_url,
        uri=song.uri
    )
    if not shared_song:
        raise HTTPException(status_code=400, detail="Failed to share song.")
    
    return {"message": "Song shared successfully", "shared_song": shared_song}