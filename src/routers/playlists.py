from asyncio.log import logger
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.crud import add_song_to_playlist, create_playlist, remove_song_from_playlist
from src.database import get_db
from src.models import User, Song
from src.schedulers.tasks import recreate_daily_playlist
from src.schemas import PlaylistCreate, PlaylistResponse, SongAddRequest, SongInPlaylist, SongResponse
from src.auth.dependencies import get_current_user

router = APIRouter()

# 24시간 내 공유된 음악으로 오늘의 플레이리스트 생성
@router.post("/today", response_model=PlaylistResponse)
async def create_today_playlist_route(db: AsyncSession = Depends(get_db)):
    try:
        shared_songs, playlist_id = await recreate_daily_playlist(db)

        # 노래 없으면 에러 반환
        if not shared_songs:
            raise HTTPException(status_code=404, detail="No songs shared in the past 24 hours")

        return PlaylistResponse(
            playlistId=playlist_id,
            name="Today's Playlist",
            playlist_type="daily",
            createdAt=datetime.utcnow(),
            tracks=[SongInPlaylist(**song.to_dict()) for song in shared_songs]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
# 오늘의 플레이리스트 생성 테스트용 추가 API
@router.post("/today/test")
async def test_create_today_playlists_route(db: AsyncSession = Depends(get_db)):
    try:
        shared_songs, playlist_id = await recreate_daily_playlist(db)
        return {"message": "Daily playlists recreated successfully for testing."}
    except Exception as e:
        logger.error(f"Error in recreate_today_playlists: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# 마이플레이리스트 생성
@router.post("/my/{user_id}", response_model=PlaylistResponse)
async def create_playlist_endpoint(
    user_id: int,  
    playlist: PlaylistCreate,  # 요청 본문에서 name 받기
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # playlist_type을 'my'로 설정
        playlist.playlist_type = 'my'
        
        # 플레이리스트 생성
        created_playlist = await create_playlist(db=db, playlist_create=playlist, user_id=user_id)

        # PlaylistResponse 형식으로 반환
        playlist_response = PlaylistResponse(
            playlistId=created_playlist.playlistId,
            name=created_playlist.name,
            playlist_type=created_playlist.playlist_type,
            createdAt=created_playlist.createdAt,
            tracks=[]  # 노래 목록은 초기 생성 시 비어 있음
        )
        return playlist_response

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

    
@router.put("/{playlistId}", response_model=SongResponse)
async def update_playlist(playlistId: int, request: SongAddRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return await add_song_to_playlist(db, playlistId, request.songId)
    except HTTPException as e:
        raise e
    
    
@router.delete("/{playlistId}", response_model=SongResponse)
async def delete_song_from_playlist(playlistId: int, request: SongAddRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return await remove_song_from_playlist(db, playlistId, request.songId)
    except HTTPException as e:
        raise e