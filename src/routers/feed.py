# src/routers/feed.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import asc
from src.database import get_db
from src.models import User, Follow, Song
from src.schemas import UserFeedResponse
from typing import List
from src.auth.dependencies import get_current_user

router = APIRouter()

@router.get("/{user_id}", response_model=List[UserFeedResponse])
async def get_user_feed(
    user_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    사용자가 팔로우하는 유저들이 공유한 음악을 오래된 순서대로 조회하는 엔드포인트.
    """
    # 해당 유저가 팔로우하는 유저 ID 목록 가져오기
    following_result = await db.execute(
        select(Follow.following_id).where(Follow.follower_id == user_id)
    )
    following_ids = [row[0] for row in following_result.fetchall()]

    # 자신도 포함
    following_ids.append(user_id)
    following_ids = list(set(following_ids))  # 중복 제거

    if not following_ids:
        raise HTTPException(status_code=404, detail="No following users or shared songs found.")

    # 팔로우한 유저들이 공유한 노래를 한 번에 가져와 오래된 순서로 정렬
    shared_songs_result = await db.execute(
        select(Song, User)
        .join(User, Song.sharedBy == User.userId)
        .where(Song.sharedBy.in_(following_ids))
        .order_by(asc(Song.sharedAt))  # 노래 공유 시간 기준으로 정렬
    )
    shared_songs = shared_songs_result.fetchall()

    if not shared_songs:
        raise HTTPException(status_code=404, detail="No songs shared by following users.")

    # 반환 데이터 구성
    feed = []
    for song, user in shared_songs:
        feed.append({
            "id": user.userId,
            "name": user.name,
            "profileImage": user.profile_image_url,
            "Song": {  # 단일 객체로 반환
                "title": song.title,
                "artist": song.artist,
                "album_cover_url": song.album_cover_url,
                "shared_at": song.sharedAt.isoformat(),  # ISO 포맷으로 변환
                "reaction": song.reaction,
                "spotify_url": song.spotify_url,
                "uri": song.uri
            }
        })

    return feed