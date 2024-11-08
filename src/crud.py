# src/crud.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime, timedelta
from src.models import User, Song, Follow, Playlist
from typing import Optional, List


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
    """ 일간 차트: 하루 동안 공유된 노래의 공유 횟수를 집계합니다. """
    today = datetime.utcnow().date()
    result = await db.execute(
        select(Song.title, Song.artist,Song.uri, func.count(Song.songId).label('share_count'))
        .filter(func.date(Song.sharedAt) == today)
        .group_by(Song.title, Song.artist, Song.uri)
        .order_by(func.count(Song.songId).desc())
    )
    # 필요한 만큼의 데이터를 가져오기 (예: 10개)
    return result.fetchmany(10)

async def get_weekly_chart(db: AsyncSession):
    """ 주간 차트: 일주일 동안 공유된 노래의 공유 횟수를 집계합니다. """
    start_of_week = datetime.utcnow().date() - timedelta(days=datetime.utcnow().date().weekday())
    result = await db.execute(
        select(Song.title, Song.artist, Song.uri,func.count(Song.songId).label('share_count'))
        .filter(func.date(Song.sharedAt) >= start_of_week)
        .group_by(Song.title, Song.artist, Song.uri)
        .order_by(func.count(Song.songId).desc())
    )
    # 필요한 만큼의 데이터를 가져오기 (예: 10개)
    return result.fetchmany(10)

async def get_monthly_chart(db: AsyncSession):
    """ 월간 차트: 한 달 동안 공유된 노래의 공유 횟수를 집계합니다. """
    start_of_month = datetime.utcnow().replace(day=1).date()
    result = await db.execute(
        select(Song.title, Song.artist, Song.uri,func.count(Song.songId).label('share_count'))
        .filter(func.date(Song.sharedAt) >= start_of_month)
        .group_by(Song.title, Song.artist, Song.uri)
        .order_by(func.count(Song.songId).desc())
    )
    # 필요한 만큼의 데이터를 가져오기 (예: 10개)
    return result.fetchmany(10)


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
