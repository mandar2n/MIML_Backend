# src/models.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# 중간 테이블 정의 (차트와 노래의 다대다 관계)
chart_songs = Table(
    "chart_songs",
    Base.metadata,
    Column("chart_id", Integer, ForeignKey("charts.chartId"), primary_key=True),
    Column("song_id", Integer, ForeignKey("songs.songId"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    userId = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_pw = Column(String, nullable=False)  # 변수명 변경: hashed_password -> hashed_pw
    name = Column(String, nullable=False)
    profile_image_url = Column(String, nullable=True)  # 프로필 이미지 URL 필드 유지
    createdAt = Column(DateTime, default=datetime.utcnow)  # 변수명 변경: created_at -> createdAt

    songs = relationship("Song", back_populates="user")
    followers = relationship("Follow", back_populates="follower", foreign_keys='Follow.follower_id')
    following = relationship("Follow", back_populates="following", foreign_keys='Follow.following_id')
    playlists = relationship("Playlist", back_populates="user")


class Song(Base):
    __tablename__ = "songs"

    songId = Column(Integer, primary_key=True, index=True)  # 변수명 변경: id -> songId
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    album = Column(String, nullable=False)
    spotify_url = Column(String, nullable=False)
    album_cover_url = Column(String, nullable=True)
    uri = Column(String, nullable=True)
    sharedBy = Column(Integer, ForeignKey("users.userId"))  # 변수명 변경: shared_by -> sharedBy
    sharedAt = Column(DateTime, default=datetime.utcnow)  # 변수명 변경: shared_at -> sharedAt

    user = relationship("User", back_populates="songs")
    charts = relationship("Chart", secondary=chart_songs, back_populates="songs")


class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.userId"), nullable=False)
    following_id = Column(Integer, ForeignKey("users.userId"), nullable=False)
    followedAt = Column(DateTime, default=datetime.utcnow)  # 변수명 변경: followed_at -> followedAt

    follower = relationship("User", back_populates="followers", foreign_keys=[follower_id])
    following = relationship("User", back_populates="following", foreign_keys=[following_id])


class Playlist(Base):
    __tablename__ = "playlists"

    playlistId = Column(Integer, primary_key=True, index=True)  # 변수명 변경: id -> playlistId
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.userId"))  # 변수명 유지
    createdAt = Column(DateTime, default=datetime.utcnow)  # 변수명 변경: created_at -> createdAt

    user = relationship("User", back_populates="playlists")


class Chart(Base):
    __tablename__ = "charts"

    chartId = Column(Integer, primary_key=True, index=True)  # 변수명 변경: id -> chartId
    chartType = Column(String, nullable=False)  # 변수명 변경: chart_type -> chartType
    generatedAt = Column(DateTime, default=datetime.utcnow)  # 변수명 변경: generated_at -> generatedAt

    songs = relationship("Song", secondary=chart_songs, back_populates="charts")
