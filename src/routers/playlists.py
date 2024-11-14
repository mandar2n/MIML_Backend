from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.crud import add_song_to_playlist, create_playlist, get_today_playlist, remove_song_from_playlist
from src.database import get_db
from src.models import User, Song
from src.schemas import PlaylistCreate, PlaylistResponse, SongAddRequest, SongInPlaylist, SongResponse

router = APIRouter()

# 24시간 내 공유된 음악으로 오늘의 플레이리스트 제공
@router.get("/today/{user_id}", response_model=PlaylistResponse)
async def get_today_playlist_route(user_id: int, db: AsyncSession = Depends(get_db)):
    
    # get_today_playlist에서 반환한 결과 그대로 반환
    shared_songs = await get_today_playlist(user_id, db)
    now = datetime.utcnow()
    
    # PlaylistResponse 형식으로 변환하여 반환
    playlist = PlaylistResponse(
        playlistId=0,  # 'Today's Playlist'에는 ID가 없으므로 0으로 설정
        name="Today's Playlist",
        createdAt=now,
        tracks=[SongInPlaylist(**song.to_dict()) for song in shared_songs]  # SongInPlaylist 스키마로 변환
    )
    return playlist

@router.post("/my/{user_id}", response_model=dict)
async def create_playlist_endpoint(
    user_id: int,  # URL 파라미터로 userId 받기
    playlist: PlaylistCreate,  # 요청 본문에서 name 받기
    db: AsyncSession = Depends(get_db)
):
    try:
        # 플레이리스트 생성
        created_playlist = await create_playlist(db=db, playlist_create=playlist, user_id=user_id)

        # PlaylistResponse 형식으로 반환
        playlist_response = {
            "playlistId": created_playlist.playlistId,
            "message": "Playlist created successfully."
        }

        return playlist_response

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

    
@router.put("/{playlistId}", response_model=SongResponse)
async def update_playlist(playlistId: int, request: SongAddRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await add_song_to_playlist(db, playlistId, request.songId)
    except HTTPException as e:
        raise e
    
    
@router.delete("/{playlistId}", response_model=SongResponse)
async def delete_song_from_playlist(playlistId: int, request: SongAddRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await remove_song_from_playlist(db, playlistId, request.songId)
    except HTTPException as e:
        raise e