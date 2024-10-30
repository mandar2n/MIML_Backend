# src/schemas.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SongBase(BaseModel):
    """
    노래의 기본 정보를 담는 스키마
    """
    title: str
    artist: str
    album: Optional[str] = None
    spotify_url: str
    album_cover_url: Optional[str] = None
    uri: Optional[str] = None

class SongCreate(SongBase):
    """
    노래를 생성할 때 사용하는 스키마
    """
    shared_by: int

class SongResponse(SongBase):
    """
    응답으로 사용할 노래 스키마
    """
    id: int
    shared_at: datetime
    shared_by: int

    class Config:
        orm_mode = True  # ORM 모델을 기반으로 직렬화 가능하도록 설정

class UserBase(BaseModel):
    """
    사용자 기본 정보를 담는 스키마
    """
    email: str
    name: str

class UserCreate(UserBase):
    """
    사용자 생성 시 사용하는 스키마
    """
    password: str

class UserResponse(UserBase):
    """
    사용자 응답 데이터의 스키마
    """
    id: int
    created_at: datetime

    class Config:
        orm_mode = True  # ORM 모델을 기반으로 직렬화 가능하도록 설정

class SongShare(BaseModel):
    """
    사용자가 노래를 공유할 때 사용하는 스키마
    """
    user_id: int
    title: str
    artist: str
    album: Optional[str] = None
    spotify_url: str
    album_cover_url: Optional[str] = None
    uri: Optional[str] = None