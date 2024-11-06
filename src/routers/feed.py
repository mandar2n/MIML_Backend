from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database import get_db
from src.models import User, Follow, Song
from src.schemas import SongResponse
from typing import List

router = APIRouter()

@router.get("/{user_id}", response_model=List[SongResponse])
async def get_user_feed(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    사용자가 팔로우하는 유저들이 공유한 음악을 피드로 조회하는 엔드포인트.
    """
    # 해당 유저가 팔로우하는 유저 ID 목록을 가져옴
    following_result = await db.execute(
        select(Follow.following_id).where(Follow.follower_id == user_id)
    )
    following_ids = [row[0] for row in following_result.fetchall()]

    if not following_ids:
        raise HTTPException(status_code=404, detail="Following users not found")

    # 팔로우한 유저들이 공유한 노래 목록 조회
    shared_songs_result = await db.execute(
        select(Song)
        .where(Song.shared_by.in_(following_ids))
        .order_by(Song.shared_at.desc())  # 최신 공유 순으로 정렬
    )
    shared_songs = shared_songs_result.scalars().all()

    return shared_songs