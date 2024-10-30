# src/models.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# 중간 테이블 정의 (차트와 노래의 다대다 관계)
chart_songs = Table(
    "chart_songs",
    Base.metadata,
    Column("chart_id", Integer, ForeignKey("charts.id"), primary_key=True),
    Column("song_id", Integer, ForeignKey("songs.id"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    songs = relationship("Song", back_populates="user")
    followers = relationship("Follow", back_populates="follower", foreign_keys='Follow.follower_id')
    following = relationship("Follow", back_populates="following", foreign_keys='Follow.following_id')
    playlists = relationship("Playlist", back_populates="user")


class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    album = Column(String, nullable=False)
    release_date = Column(DateTime)
    spotify_url = Column(String, nullable=False)
    album_cover_url = Column(String, nullable=True)
    uri = Column(String, nullable=True)
    shared_by = Column(Integer, ForeignKey("users.id"))
    shared_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="songs")
    charts = relationship("Chart", secondary=chart_songs, back_populates="songs")


class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    following_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    followed_at = Column(DateTime, default=datetime.utcnow)

    follower = relationship("User", back_populates="followers", foreign_keys=[follower_id])
    following = relationship("User", back_populates="following", foreign_keys=[following_id])


class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="playlists")


class Chart(Base):
    __tablename__ = "charts"

    id = Column(Integer, primary_key=True, index=True)
    chart_type = Column(String, nullable=False)  # e.g., daily, weekly, monthly
    generated_at = Column(DateTime, default=datetime.utcnow)

    songs = relationship("Song", secondary=chart_songs, back_populates="charts")