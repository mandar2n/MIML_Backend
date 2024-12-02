from asyncio.log import logger
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.crud import add_song_to_playlist, create_playlist, get_playlist_by_type, remove_song_from_playlist
from src.database import get_db
from src.models import User, Song
from src.schedulers.tasks import recreate_daily_playlist
from src.schemas import PlaylistCreate, PlaylistResponse, SongAddRequest, SongInPlaylist, SongRemoveRequest, SongResponse
from src.auth.dependencies import get_current_user

router = APIRouter()

# 24시간 내 공유된 음악으로 오늘의 플레이리스트 생성 (스케줄러 api)
@router.post("/today", response_model=dict)
async def create_today_playlist_route(db: AsyncSession = Depends(get_db)):
    """
    스케줄러에서 매일 특정 시각에 호출되는 API.
    실제 데이터베이스에 커밋하여 오늘의 플레이리스트를 생성.
    """
    try:
        # 매일 24시간 기준으로 모든 유저의 플레이리스트 생성
        await recreate_daily_playlist(db, is_test=False)
        return {"message": "Daily playlists recreated successfully."}
    except Exception as e:
        logger.error(f"Error in recreate_today_playlists: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    
# 오늘의 플레이리스트 생성 테스트용 API
@router.post("/today/test", response_model=dict)
async def test_create_today_playlists_route(db: AsyncSession = Depends(get_db)):
    """
    테스트를 위해 호출되는 API.
    데이터베이스에 커밋하지 않으며 디버깅 정보를 반환.
    """
    try:
        # 트랜잭션을 롤백하여 데이터베이스를 변경하지 않음
        result = await recreate_daily_playlist(db, is_test=True)

        # 디버깅 정보를 포함한 반환
        return {
            "message": "Daily playlists recreated successfully for testing.",
            "details": {
                "total_users_processed": len(result.get("users", [])),
                "playlists_created": len(result.get("playlists", [])),
                "shared_songs_processed": result.get("shared_songs", 0),
            },
        }
    except Exception as e:
        logger.error(f"Error in test_create_today_playlists: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# 마이 플레이리스트 생성
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


# 마이 플레이리스트에 특정 노래 추가
@router.put("/{playlistId}/add", response_model=SongResponse)
async def update_playlist(
    playlistId: int, 
    request: SongAddRequest, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    try:
        return await add_song_to_playlist(db, playlistId, request.uri)
    except HTTPException as e:
        raise e
    
    
# 마이 플레이리스트에 특정 노래 삭제
@router.delete("/{playlistId}/remove", response_model=SongResponse)
async def delete_song_from_playlist(
    playlistId: int, 
    request: SongRemoveRequest,
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    try:
        return await remove_song_from_playlist(db, playlistId, request.uri)
    except HTTPException as e:
        raise e
    
    
# 오늘의 플레이리스트 조회 
@router.get("/today/{userId}", response_model=PlaylistResponse)
async def get_today_playlist(userId: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    playlist = await get_playlist_by_type(userId, "daily", db)
    if not playlist:
        raise HTTPException(status_code=404, detail="Daily playlist not found.")
    return playlist


# 마이 플레이리스트 조회
@router.get("/my/{userId}", response_model=PlaylistResponse)
async def get_my_playlist(userId: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    playlist = await get_playlist_by_type(userId, "my", db)
    if not playlist:
        raise HTTPException(status_code=404, detail="My playlist not found.")
    return playlist