# src/routers/spotify.py
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.spotify_service import get_song_info, get_song_details
from src.database import get_db
from src.auth.dependencies import get_current_user
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


# @router.post("/search/{song_uri}/share")
# async def share_song_to_feed(song: SongShare, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
#     """
#     사용자가 노래를 선택하여 피드에 공유하는 엔드포인트
#     """
#     shared_song = await share_song(
#         db=db,
#         user_id=current_user.userId,
#         song_title=song.title,
#         artist=song.artist,
#         album=song.album,
#         spotify_url=song.spotify_url,
#         album_cover_url=song.album_cover_url,
#         uri=song.uri
#     )
#     if not shared_song:
#         raise HTTPException(status_code=400, detail="Failed to share song.")
    
#     return {"message": "Song shared successfully", "shared_song": shared_song}