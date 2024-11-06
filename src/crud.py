from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime, timedelta
from src.models import User, Song, Follow, Playlist
from typing import Optional


async def create_user(db: AsyncSession, email: str, hashed_password: str, name: str, profile_image_url: Optional[str] = None):
    user = User(
        email=email,
        hashed_password=hashed_password,
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


async def create_song(db: AsyncSession, title: str, artist: str, album: str, spotify_url: str, shared_by: int):
    song = Song(title=title, artist=artist, album=album, spotify_url=spotify_url, shared_by=shared_by)
    db.add(song)
    await db.commit()
    await db.refresh(song)
    return song


async def get_daily_chart(db: AsyncSession):
    """ 일간 차트: 하루 동안 공유된 노래의 공유 횟수를 집계합니다. """
    today = datetime.utcnow().date()
    result = await db.execute(
        select(Song.title, Song.artist, func.count(Song.id).label('share_count'))
        .filter(func.date(Song.shared_at) == today)
        .group_by(Song.title, Song.artist)
        .order_by(func.count(Song.id).desc())
    )
    return result.all()


async def get_weekly_chart(db: AsyncSession):
    """ 주간 차트: 일주일 동안 공유된 노래의 공유 횟수를 집계합니다. """
    start_of_week = datetime.utcnow().date() - timedelta(days=datetime.utcnow().date().weekday())
    result = await db.execute(
        select(Song.title, Song.artist, func.count(Song.id).label('share_count'))
        .filter(func.date(Song.shared_at) >= start_of_week)
        .group_by(Song.title, Song.artist)
        .order_by(func.count(Song.id).desc())
    )
    return result.all()


async def get_monthly_chart(db: AsyncSession):
    """ 월간 차트: 한 달 동안 공유된 노래의 공유 횟수를 집계합니다. """
    start_of_month = datetime.utcnow().replace(day=1).date()
    result = await db.execute(
        select(Song.title, Song.artist, func.count(Song.id).label('share_count'))
        .filter(func.date(Song.shared_at) >= start_of_month)
        .group_by(Song.title, Song.artist)
        .order_by(func.count(Song.id).desc())
    )
    return result.all()


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
        shared_by=user_id,
        shared_at=datetime.utcnow()
    )

    db.add(shared_song)
    await db.commit()  # 비동기 커밋
    await db.refresh(shared_song)
    return shared_song