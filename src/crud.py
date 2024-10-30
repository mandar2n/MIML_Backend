# src/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from src.models import Song


from sqlalchemy.orm import Session
from models import User, Song, Follow, Playlist


def create_user(db: Session, email: str, hashed_password: str, name: str):
    user = User(email=email, hashed_password=hashed_password, name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_song(db: Session, title: str, artist: str, album: str, spotify_url: str, shared_by: int):
    song = Song(title=title, artist=artist, album=album, spotify_url=spotify_url, shared_by=shared_by)
    db.add(song)
    db.commit()
    db.refresh(song)
    return song

def get_daily_chart(db: Session):
    """ 일간 차트: 하루 동안 공유된 노래의 공유 횟수를 집계합니다. """
    today = datetime.utcnow().date()
    return db.query(
        Song.title, Song.artist, func.count(Song.id).label('share_count')
    ).filter(
        func.date(Song.shared_at) == today
    ).group_by(
        Song.title, Song.artist
    ).order_by(
        func.count(Song.id).desc()
    ).all()

def get_weekly_chart(db: Session):
    """ 주간 차트: 일주일 동안 공유된 노래의 공유 횟수를 집계합니다. """
    start_of_week = datetime.utcnow().date() - timedelta(days=datetime.utcnow().date().weekday())
    return db.query(
        Song.title, Song.artist, func.count(Song.id).label('share_count')
    ).filter(
        func.date(Song.shared_at) >= start_of_week
    ).group_by(
        Song.title, Song.artist
    ).order_by(
        func.count(Song.id).desc()
    ).all()

def get_monthly_chart(db: Session):
    """ 월간 차트: 한 달 동안 공유된 노래의 공유 횟수를 집계합니다. """
    start_of_month = datetime.utcnow().replace(day=1).date()
    return db.query(
        Song.title, Song.artist, func.count(Song.id).label('share_count')
    ).filter(
        func.date(Song.shared_at) >= start_of_month
    ).group_by(
        Song.title, Song.artist
    ).order_by(
        func.count(Song.id).desc()
    ).all()

def share_song(
    db: Session, 
    user_id: int, 
    song_title: str, 
    artist: str, 
    album: str, 
    spotify_url: str, 
    album_cover_url: str, 
    uri: str
):
    """
    공유된 노래를 데이터베이스에 추가합니다.
    """
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
    db.commit()
    db.refresh(shared_song)
    return shared_song