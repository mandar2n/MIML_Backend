from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database import get_db
from src.schemas import UserCreate, UserResponse, FollowRequest, SongResponse
from src.models import User, Follow, Song
from src.crud import create_user, get_user_by_email, search_user_by_name, add_follow
from typing import List

router = APIRouter()

@router.post("/profile", response_model=UserResponse)
async def create_profile(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = await create_user(
        db=db,
        email=user.email,
        hashed_password=user.password,
        name=user.name,
        profile_image_url=user.profile_image_url
    )
    
    return new_user

@router.get("/profile/{user_id}", response_model=dict)
async def get_user_profile(user_id: int, db: AsyncSession = Depends(get_db)):
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    shared_songs_result = await db.execute(select(Song).where(Song.shared_by == user_id))
    shared_songs = shared_songs_result.scalars().all()

    return {
        "user": {
            "email": user.email,
            "name": user.name,
            "profile_image_url": user.profile_image_url,
            "created_at": user.created_at
        },
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

@router.get("/profile/{user_id}/following", response_model=List[UserResponse])
async def get_following_list(user_id: int, db: AsyncSession = Depends(get_db)):
    following_result = await db.execute(select(User).join(Follow, Follow.following_id == User.id).where(Follow.follower_id == user_id))
    following_users = following_result.scalars().all()

    if not following_users:
        raise HTTPException(status_code=404, detail="No following users found")

    return following_users

@router.get("/profile/{user_id}/followers", response_model=List[UserResponse])
async def get_followers_list(user_id: int, db: AsyncSession = Depends(get_db)):
    followers_result = await db.execute(select(User).join(Follow, Follow.follower_id == User.id).where(Follow.following_id == user_id))
    followers = followers_result.scalars().all()

    if not followers:
        raise HTTPException(status_code=404, detail="No followers found")

    return followers

@router.post("/{user_id}/follow")
async def follow_user(user_id: int, request: FollowRequest, db: AsyncSession = Depends(get_db)):
    follower_id = request.follower_id

    if user_id == follower_id:
        raise HTTPException(status_code=400, detail="You cannot follow yourself.")
    
    follow = await add_follow(db, follower_id=follower_id, following_id=user_id)
    
    return {"message": "Followed successfully", "follow": follow}