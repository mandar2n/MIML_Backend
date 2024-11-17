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
    # album: Optional[str] = None
    # spotify_url: str
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
    songId: int
    sharedAt: datetime
    sharedBy: int

    class Config:
        orm_mode = True  # ORM 모델을 기반으로 직렬화 가능하도록 설정


class SongDetailResponse(BaseModel):
    """
    노래 상세 정보 스키마
    """
    title: str
    artist: str
    album: str
    spotify_url: str
    album_cover_url: Optional[str] = None
    uri: str

    class Config:
        orm_mode = True
class UserBase(BaseModel):
    """
    사용자 기본 정보를 담는 스키마
    """
    email: str
    name: str
    profile_image_url: Optional[str] = None  # 프로필 이미지 URL 필드 추가

class UserCreate(UserBase):
    """
    사용자 생성 시 사용하는 스키마
    """
    password: str

class UserResponse(UserBase):
    """
    사용자 응답 데이터의 스키마
    """
    userId: int
    createdAt: datetime

    class Config:
        orm_mode = True  # ORM 모델을 기반으로 직렬화 가능하도록 설정

class UserUpdate(BaseModel):
    email: Optional[str]
    password: Optional[str]
    name: Optional[str]
    profile_image_url: Optional[str]

    class Config:
        orm_mode = True

class SharedSongDetail(BaseModel):
    """
    공유된 노래의 세부 정보를 담는 스키마
    """
    title: str
    artist: str
    album_cover_url: Optional[str] = None
    shared_at: datetime
    reaction: Optional[int] = 0
    spotify_url: str
    uri: str

    class Config:
        orm_mode = True

class UserFeedResponse(BaseModel):
    """
    사용자의 정보와 공유된 노래 목록을 담는 스키마
    """
    id: int
    name: str
    profileImage: Optional[str] = None
    Song: List[SharedSongDetail]

    class Config:
        orm_mode = True


class FollowerInfo(BaseModel):
    userId: int
    name: str
    profile_image_url: Optional[str]

class UserProfileWithFollowers(BaseModel):
    userId: int
    email: str
    name: str
    profile_image_url: Optional[str]
    createdAt: datetime
    followers: List[FollowerInfo]
    following: List[FollowerInfo]

    class Config:
        orm_mode = True

class FollowRequest(BaseModel):
    follower_id: int

class SongShare(BaseModel):
    """
    사용자가 노래를 공유할 때 사용하는 스키마
    """
    title: str
    artist: str
    album: Optional[str] = None
    spotify_url: str
    album_cover_url: Optional[str] = None
    uri: Optional[str] = None
    
class ChartResponse(BaseModel):
    """
    차트 응답을 위한 스키마
    """
    rank: int
    title: str
    artist: str
    uri: str  
    album_cover_url: Optional[str]  # 앨범 커버 URL 필드 추가
    share_count: int

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    profile_image_url: Optional[str] = "default_image_url"  # 기본값 설정

class LoginRequest(BaseModel):
    email: str
    password: str
    
class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    userId: int
    
# Playlist 생성 요청에 대한 스키마
class PlaylistCreate(BaseModel):
    name: str
    song_ids: Optional[List[int]] = []  # 플레이리스트에 추가할 노래 ID 목록
    playlist_type: str  # 'daily' 또는 'my'

# Playlist 응답에 대한 스키마
class SongInPlaylist(BaseModel):
    songId: int
    title: str
    artist: str
    album: str
    spotify_url: str
    album_cover_url: Optional[str]
    uri: Optional[str]
    sharedBy: int
    sharedAt: datetime

    class Config:
        orm_mode = True  # SQLAlchemy 모델과의 호환성

class PlaylistResponse(BaseModel):
    playlistId: int
    name: str
    playlist_type: str
    createdAt: datetime
    tracks: List[SongInPlaylist]  # 플레이리스트에 포함된 노래 목록

    class Config:
        orm_mode = True
        
class SongAddRequest(BaseModel):
    songId: int

class SongResponse(BaseModel):
    message: str
        