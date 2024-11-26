# src/crud.py

from sqlite3 import IntegrityError
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime, timedelta
from src.models import User, Song, Follow, Playlist
from typing import Optional, List
from src.schemas import PlaylistCreate, UserUpdate
from src.auth.security import get_password_hash
import logging

logger = logging.getLogger(__name__)

async def create_user(db: AsyncSession, email: str, hashed_password: str, name: str, profile_image_url: Optional[str] = None):
    user = User(
        email=email,
        hashed_pw=hashed_password,  # 컬럼명이 변경됨
        name=name,
        profile_image_url=profile_image_url  # 프로필 이미지 URL 설정
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def update_user_profile(db: AsyncSession, user_id: int, user_update: UserUpdate):
    result = await db.execute(select(User).where(User.userId == user_id))
    user = result.scalars().first()

    if not user:
        return None

    # 업데이트할 데이터만 갱신
    if user_update.email:
        user.email = user_update.email
    if user_update.password:
        user.hashed_pw = get_password_hash(user_update.password)
    if user_update.name:
        user.name = user_update.name
    if user_update.profile_image_url:
        user.profile_image_url = user_update.profile_image_url

    await db.commit()
    await db.refresh(user)

    return user

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def search_user_by_name(db: AsyncSession, name: str) -> List[User]:
    result = await db.execute(select(User).filter(User.name.ilike(f"%{name}%")))
    return result.scalars().all()

async def add_follow(db: AsyncSession, follower_id: int, following_id: int):
    follow = Follow(follower_id=follower_id, following_id=following_id)
    db.add(follow)
    await db.commit()
    await db.refresh(follow)
    return follow


async def create_song(db: AsyncSession, title: str, artist: str, album: str, spotify_url: str, shared_by: int):
    song = Song(
        title=title,
        artist=artist,
        album=album,
        spotify_url=spotify_url,
        sharedBy=shared_by  # 컬럼명이 변경됨
    )
    db.add(song)
    await db.commit()
    await db.refresh(song)
    return song


async def get_daily_chart(db: AsyncSession):
    """ 일간 차트: 하루 동안 공유된 노래의 공유 횟수를 집계하고 순위를 부여합니다. """
    today = datetime.utcnow().date()
    result = await db.execute(
        select(Song.title, Song.artist, Song.uri, Song.album_cover_url, func.count(Song.songId).label('share_count'))
        .filter(func.date(Song.sharedAt) == today)
        .group_by(Song.title, Song.artist, Song.uri, Song.album_cover_url)
        .order_by(func.count(Song.songId).desc())
    )
    # 순위를 기반으로 ID 추가
    chart_data = result.fetchmany(10)
    return [
        {
            "rank": idx + 1,  # 순위 기반 ID
            "title": row.title,
            "artist": row.artist,
            "uri": row.uri,
            "album_cover_url": row.album_cover_url,
            "share_count": row.share_count
        }
        for idx, row in enumerate(chart_data)
    ]

async def get_weekly_chart(db: AsyncSession):
    """ 주간 차트: 일주일 동안 공유된 노래의 공유 횟수를 집계하고 순위를 부여합니다. """
    start_of_week = datetime.utcnow().date() - timedelta(days=datetime.utcnow().date().weekday())
    result = await db.execute(
        select(Song.title, Song.artist, Song.uri, Song.album_cover_url, func.count(Song.songId).label('share_count'))
        .filter(func.date(Song.sharedAt) >= start_of_week)
        .group_by(Song.title, Song.artist, Song.uri, Song.album_cover_url)
        .order_by(func.count(Song.songId).desc())
    )
    # 순위를 기반으로 ID 추가
    chart_data = result.fetchmany(10)
    return [
        {
            "rank": idx + 1,  # 순위 기반 ID
            "title": row.title,
            "artist": row.artist,
            "uri": row.uri,
            "album_cover_url": row.album_cover_url,
            "share_count": row.share_count
        }
        for idx, row in enumerate(chart_data)
    ]


async def get_monthly_chart(db: AsyncSession):
    """ 월간 차트: 한 달 동안 공유된 노래의 공유 횟수를 집계하고 순위를 부여합니다. """
    start_of_month = datetime.utcnow().replace(day=1).date()
    result = await db.execute(
        select(Song.title, Song.artist, Song.uri, Song.album_cover_url, func.count(Song.songId).label('share_count'))
        .filter(func.date(Song.sharedAt) >= start_of_month)
        .group_by(Song.title, Song.artist, Song.uri, Song.album_cover_url)
        .order_by(func.count(Song.songId).desc())
    )
    # 순위를 기반으로 ID 추가
    chart_data = result.fetchmany(10)
    return [
        {
            "rank": idx + 1,  # 순위 기반 ID
            "title": row.title,
            "artist": row.artist,
            "uri": row.uri,
            "album_cover_url": row.album_cover_url,
            "share_count": row.share_count
        }
        for idx, row in enumerate(chart_data)
    ]

async def share_song(
    db: AsyncSession,
    user_id: int,
    song_title: str,
    artist: str,
    album: str,
    spotify_url: str,
    album_cover_url: str,
    uri: str
):
    shared_song = Song(
        title=song_title,
        artist=artist,
        album=album,
        spotify_url=spotify_url,
        album_cover_url=album_cover_url,
        uri=uri,
        sharedBy=user_id,  # 컬럼명이 변경됨
        sharedAt=datetime.utcnow()  # 컬럼명이 변경됨
    )
    
    db.add(shared_song)
    await db.commit()  # 비동기 커밋
    await db.refresh(shared_song)
    return shared_song

# async def create_today_playlist(user_id: int, db: AsyncSession) -> List[Song]:
#     try:
#         now = datetime.utcnow()
#         # 한국 시간 18시 (UTC 기준 9시)에 플레이리스트 생성
#         if now.hour < 1:
#             raise HTTPException(status_code=400, detail="Today's playlist is only available after 18:00")

#         # 지난 24시간 기준으로 시작 시각 계산
#         past_24_hours = now - timedelta(hours=24)

#         # 트랜잭션 내에서 비동기 작업 수행
#         async with db.begin():
#             # 사용자 검색
#             user_result = await db.execute(select(User).where(User.userId == user_id))
#             user = user_result.scalar_one_or_none()
#             if not user:
#                 raise HTTPException(status_code=404, detail="User not found")

#             # 사용자가 팔로우하는 유저들의 ID 가져오기
#             followed_user_ids_result = await db.execute(
#                 select(Follow.following_id).where(Follow.follower_id == user_id)
#             )
#             followed_user_ids = [row.following_id for row in followed_user_ids_result]

#             if not followed_user_ids:
#                 followed_user_ids = []  # 빈 리스트로 처리

#             # 24시간 내 공유된 노래들 조회
#             shared_songs_result = await db.execute(
#                 select(Song).where(
#                     Song.sharedAt >= past_24_hours,
#                     Song.sharedBy.in_([user_id] + followed_user_ids)
#                 )
#             )
#             shared_songs = shared_songs_result.scalars().all()
            
         
#             # 오늘의 플레이리스트 생성
#             playlist = Playlist(
#                 name="Today's Playlist",
#                 playlist_type="daily",
#                 createdAt=datetime.utcnow(),
#                 user_id=user_id
#             )
#             db.add(playlist)

#         # 비동기 작업이 끝난 후 commit() 및 refresh() 호출
#         await db.commit()  # 트랜잭션 커밋
#         await db.refresh(playlist)  # 트랜잭션이 닫힌 후에 refresh 호출

#         # 생성된 playlistId 반환
#         return shared_songs, playlist.playlistId
    
#     except Exception as e:
#         logger.error(f"Error in create_today_playlist: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

async def create_playlist(db: AsyncSession, playlist_create: PlaylistCreate, user_id: int):
    playlist_type = playlist_create.playlist_type
    try:
        # 한 사용자가 이미 마이 플레이리스트를 가지고 있는지 확인
        existing_playlist = await db.execute(
            select(Playlist).where(
                Playlist.user_id == user_id,
                Playlist.playlist_type == 'my'
            )
        )
        existing_playlist = existing_playlist.scalar_one_or_none()

        if existing_playlist:
            raise HTTPException(
                status_code=400,
                detail=f"User already has a {playlist_type} playlist. Cannot create another one."
            )

        # 새로운 플레이리스트 생성
        new_playlist = Playlist(
            name=playlist_create.name,
            user_id=user_id,
            playlist_type=playlist_type,
            createdAt=datetime.utcnow()
        )

        db.add(new_playlist)
        await db.commit()
        await db.refresh(new_playlist)
        return new_playlist
    
    except HTTPException as e:
        # FastAPI가 HTTPException을 처리하도록 바로 반환
        raise e

    except Exception as e:
        # 예상치 못한 오류만 500으로 처리
        logger.error(f"Unexpected error in create_playlist_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
    
async def add_song_to_playlist(db: AsyncSession, playlist_id: int, song_id: int):
    try:
        result = await db.execute(select(Song).filter(Song.songId == song_id)) # 해당 노래가 songs 테이블에 존재하는지 확인
        song = result.scalar_one_or_none()
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")

        playlist_result = await db.execute(select(Playlist).where(Playlist.playlistId == playlist_id))
        playlist = playlist_result.scalar_one_or_none()
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        # 노래 추가
        playlist.songs.append(song)
        await db.commit()
        return {"message": "Song added to playlist successfully"}
    except Exception as e:
        logger.error(f"Error in add_song_to_playlist: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def remove_song_from_playlist(db: AsyncSession, playlist_id: int, song_id: int):
    try:
        playlist_result = await db.execute(select(Playlist).where(Playlist.playlistId == playlist_id))
        playlist = playlist_result.scalar_one_or_none()
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        song = next((s for s in playlist.songs if s.songId == song_id), None)
        if not song:
            raise HTTPException(status_code=404, detail="Song not found in the playlist")

        # 노래 삭제
        playlist.songs.remove(song)
        await db.commit()
        return {"message": "Song removed from playlist successfully"}
    except Exception as e:
        logger.error(f"Error in remove_song_from_playlist: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")