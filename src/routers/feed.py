# src/routers/feed.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database import get_db
from src.models import User, Follow, Song
from src.schemas import UserFeedResponse
from typing import List
from src.auth.dependencies import get_current_user

router = APIRouter()

@router.get("/{user_id}", response_model=List[UserFeedResponse])
async def get_user_feed(user_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    사용자가 팔로우하는 유저들과 자신의 공유한 음악을 피드로 조회하는 엔드포인트.
    공유된 노래가 없는 사용자는 제외.
    """
    # 팔로우하고 있는 사용자 ID 가져오기
    following_result = await db.execute(
        select(Follow.following_id).where(Follow.follower_id == user_id)
    )
    following_ids = [row[0] for row in following_result.fetchall()]

    # 자신도 포함 (현재 사용자의 ID 추가)
    following_ids.append(user_id)

    # 중복 제거
    following_ids = list(set(following_ids))

    # 팔로우한 사용자 또는 자신 중 공유된 노래가 있는 사용자만 가져오기
    user_feed = []
    for following_id in following_ids:
        # 공유된 노래가 있는지 확인
        shared_songs_result = await db.execute(
            select(Song).where(Song.sharedBy == following_id).order_by(Song.sharedAt.desc())
        )
        shared_songs = shared_songs_result.scalars().all()

        # 공유된 노래가 있는 경우만 추가
        if shared_songs:
            user_result = await db.execute(select(User).where(User.userId == following_id))
            user = user_result.scalars().first()

            if user:
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

    if not user_feed:
        raise HTTPException(status_code=404, detail="No shared songs found from following users")

    return user_feed