from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database import get_db
from src.schemas import UserCreate, UserResponse, FollowRequest , SongResponse
from src.models import User, Follow, Song
from src.crud import create_user,get_user_by_email,search_user_by_name,add_follow
from typing import List


router = APIRouter()

@router.post("/profile", response_model=UserResponse)
async def create_profile(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 프로필 이미지 URL이 포함된 사용자 생성
    new_user = await create_user(
        db=db,
        email=user.email,
        hashed_password=user.password,
        name=user.name,
        profile_image_url=user.profile_image_url  # 프로필 이미지 URL 전달
    )
    
    return new_user

@router.put("/profile/{user_id}", response_model=UserResponse)
async def update_profile(user_id: int, user: UserCreate, db: AsyncSession = Depends(get_db)):
    # 기존 사용자 정보 가져오기
    result = await db.execute(select(User).filter(User.id == user_id))
    db_user = result.scalars().first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 이메일 중복 체크
    if user.email != db_user.email:
        existing_user = await get_user_by_email(db, email=user.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

    # 사용자 정보 업데이트
    db_user.email = user.email
    db_user.name = user.name
    db_user.profile_image_url = user.profile_image_url

    # 변경 사항 커밋
    await db.commit()
    await db.refresh(db_user)

    return db_user

@router.get("/profile/{user_id}", response_model=dict)
async def get_user_profile(user_id: int, db: AsyncSession = Depends(get_db)):
    # 유저 정보 조회
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 유저가 팔로잉하는 사람 목록
    following_result = await db.execute(select(User).join(Follow, Follow.following_id == User.id).where(Follow.follower_id == user_id))
    following_users = following_result.scalars().all()

    # 유저를 팔로우하는 사람 목록
    followers_result = await db.execute(select(User).join(Follow, Follow.follower_id == User.id).where(Follow.following_id == user_id))
    followers = followers_result.scalars().all()

    # 유저가 공유한 노래 목록
    shared_songs_result = await db.execute(select(Song).where(Song.shared_by == user_id))
    shared_songs = shared_songs_result.scalars().all()

    return {
        "user": {
            "email": user.email,
            "name": user.name,
            "profile_image_url": user.profile_image_url,
            "created_at": user.created_at
        },
        "following": [{"id": u.id, "name": u.name} for u in following_users],
        "followers": [{"id": u.id, "name": u.name} for u in followers],
        "shared_songs": [
            {
                "title": song.title,
                "artist": song.artist,
                "album": song.album,
                "spotify_url": song.spotify_url,
                "shared_at": song.shared_at
            } for song in shared_songs
        ]
    }

@router.get("/search", response_model=List[UserResponse])
async def search_user(name: str, db: AsyncSession = Depends(get_db)):
    users = await search_user_by_name(db, name)
    if not users:
        raise HTTPException(status_code=404, detail="No users found with the given name")
    return users

@router.post("/{user_id}/follow")
async def follow_user(user_id: int, request: FollowRequest, db: AsyncSession = Depends(get_db)):
    follower_id = request.follower_id

    # 자기 자신을 팔로우하려는 경우 예외 처리
    if user_id == follower_id:
        raise HTTPException(status_code=400, detail="You cannot follow yourself.")
    
    # 팔로우 관계 추가
    follow = await add_follow(db, follower_id=follower_id, following_id=user_id)
    
    return {"message": "Followed successfully", "follow": follow}