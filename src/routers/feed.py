# src/routers/feed.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database import get_db
from src.models import User, Follow, Song
from src.schemas import UserFeedResponse
from typing import List

router = APIRouter()

@router.get("/{user_id}", response_model=List[UserFeedResponse])
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

    # 팔로우한 유저들의 정보와 공유한 노래를 가져옴
    user_feed = []
    for following_id in following_ids:
        user_result = await db.execute(select(User).where(User.userId == following_id))
        user = user_result.scalars().first()

        if user:
            # 해당 사용자가 공유한 노래 목록을 조회
            shared_songs_result = await db.execute(
                select(Song).where(Song.sharedBy == user.userId).order_by(Song.sharedAt.desc())
            )
            shared_songs = shared_songs_result.scalars().all()

            # User 정보와 노래 목록을 구성
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

    return user_feed