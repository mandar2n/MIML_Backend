from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.schemas import PlaylistCreate, PlaylistResponse

router = APIRouter()

@router.get("/today/{user_id}")
async def get_today_playlist(user_id: int, db: AsyncSession = Depends(get_db)):
    # 24시간 내 공유된 음악으로 오늘의 플레이리스트 제공
    pass  # 추후 구현 필요

@router.post("/my", response_model=PlaylistResponse)
async def create_playlist(playlist: PlaylistCreate, db: AsyncSession = Depends(get_db)):
    # 나만의 플레이리스트 생성
    pass  # 추후 구현 필요

@router.put("/{playlist_id}")
async def update_playlist(playlist_id: int, db: AsyncSession = Depends(get_db)):
    # 특정 플레이리스트에 음악 추가 또는 수정
    pass  # 추후 구현 필요