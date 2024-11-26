# src/crud.py

from sqlite3 import IntegrityError
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from src.models import User, Song, Follow, Playlist, playlist_songs
from typing import Optional, List
from src.schemas import PlaylistCreate, PlaylistResponse, UserUpdate
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
async def get_yearly_chart(db: AsyncSession):
    """ 연간 차트: 한 해 동안 공유된 노래의 공유 횟수를 집계하고 순위를 부여합니다. """
    start_of_year = datetime.utcnow().replace(month=1, day=1).date()  # 해당 연도의 시작 날짜
    result = await db.execute(
        select(Song.title, Song.artist, Song.uri, Song.album_cover_url, func.count(Song.songId).label('share_count'))
        .filter(func.date(Song.sharedAt) >= start_of_year)
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
    
# 마이플레이리스트에 노래 추가 함수
async def add_song_to_playlist(db: AsyncSession, playlist_id: int, song_id: int):
    try:
        # 노래가 존재하는지 확인
        song_result = await db.execute(select(Song).filter(Song.songId == song_id))
        song = song_result.scalar_one_or_none()
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")

        # 플레이리스트가 존재하는지 확인
        playlist_result = await db.execute(select(Playlist).filter(Playlist.playlistId == playlist_id))
        playlist = playlist_result.scalar_one_or_none()
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        # 중복 여부 확인
        existing_entry = await db.execute(
            select(playlist_songs.c.song_id)
            .where(
                playlist_songs.c.playlist_id == playlist_id,
                playlist_songs.c.song_id == song_id,
            )
        )
        if existing_entry.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Song already in the playlist")

        # 중간 테이블에 직접 추가
        await db.execute(
            playlist_songs.insert().values(playlist_id=playlist_id, song_id=song_id)
        )
        await db.commit()
        return {"message": "Song added to playlist successfully"}
    except HTTPException as e:
        # FastAPI가 자동으로 detail과 status_code를 사용자에게 전달
        raise e
    except Exception as e:
        logger.error(f"Error in add_song_to_playlist: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
# 마이플레이리스트에 노래 삭제 함수
async def remove_song_from_playlist(db: AsyncSession, playlist_id: int, song_id: int):
    try:
        # 플레이리스트가 존재하는지 확인
        playlist_result = await db.execute(select(Playlist).filter(Playlist.playlistId == playlist_id))
        playlist = playlist_result.scalar_one_or_none()
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        # 노래가 존재하는지 확인 및 삭제
        delete_query = playlist_songs.delete().where(
            playlist_songs.c.playlist_id == playlist_id,
            playlist_songs.c.song_id == song_id,
        )
        result = await db.execute(delete_query)
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Song not found in the playlist")

        await db.commit()
        return {"message": "Song removed from playlist successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in remove_song_from_playlist: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# 특정 유형의 플레이리스트를 가져오는 함수
async def get_playlist_by_type(user_id: int, playlist_type: str, db: AsyncSession) -> PlaylistResponse:
    result = await db.execute(
        select(Playlist)
        .where(Playlist.user_id == user_id, Playlist.playlist_type == playlist_type)
        .options(selectinload(Playlist.songs))  # 플레이리스트와 노래 관계를 로드
    )
    playlist = result.scalars().first()

    if not playlist:
        return None

    # PlaylistResponse 스키마로 변환
    return PlaylistResponse(
        playlistId=playlist.playlistId,
        name=playlist.name,
        playlist_type=playlist.playlist_type,
        createdAt=playlist.createdAt,
        tracks=[
            {
                "songId": song.songId,
                "title": song.title,
                "artist": song.artist,
                "album": song.album,
                "spotify_url": song.spotify_url,
                "album_cover_url": song.album_cover_url,
                "uri": song.uri,
                "sharedBy": song.sharedBy,
                "sharedAt": song.sharedAt,
            }
            for song in playlist.songs
        ],
    )