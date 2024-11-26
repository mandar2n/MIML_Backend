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

    # 팔로우한 유저들의 정보와 공유한 노래를 오래된 순서로 가져오기
    user_feed = []
    for following_id in following_ids:
        user_result = await db.execute(select(User).where(User.userId == following_id))
        user = user_result.scalars().first()

        if user:
            # 해당 사용자가 공유한 노래 목록을 오래된 순서대로 조회
            shared_songs_result = await db.execute(
                select(Song)
                .where(Song.sharedBy == user.userId)
                .order_by(asc(Song.sharedAt))  # 오래된 순으로 정렬
            )
            shared_songs = shared_songs_result.scalars().all()

            # 공유된 노래가 없는 유저는 제외
            if not shared_songs:
                continue

            # User 정보와 노래 목록 구성
            user_data = {
                "id": user.userId,
                "name": user.name,
                "profileImage": user.profile_image_url,
                "Song": [
                    {
                        "title": song.title,
                        "artist": song.artist,
                        "album_cover_url": song.album_cover_url,
                        "shared_at": song.sharedAt,
                        "reaction": song.reaction,
                        "spotify_url": song.spotify_url,
                        "uri": song.uri
                    }
                    for song in shared_songs
                ]
            }
            user_feed.append(user_data)

    # 오래된 순서로 정렬된 전체 피드 반환
    sorted_feed = sorted(
        user_feed,
        key=lambda user: user["Song"][0]["shared_at"],  # 각 유저의 가장 오래된 노래를 기준으로 정렬
    )

    return sorted_feed