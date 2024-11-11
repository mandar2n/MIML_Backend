# src/routers/users.py


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database import get_db
from src.schemas import UserCreate, UserResponse, FollowRequest, SongResponse,UserUpdate
from src.models import User, Follow, Song
from src.crud import create_user, get_user_by_email, search_user_by_name, add_follow,update_user_profile
from typing import List
from src.auth.dependencies import get_current_user

router = APIRouter()

@router.get("/profile/{user_id}", response_model=dict)
async def get_user_profile(user_id: int, db: AsyncSession = Depends(get_db)):
    user_result = await db.execute(select(User).where(User.userId == user_id))
    user = user_result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    shared_songs_result = await db.execute(select(Song).where(Song.sharedBy == user_id))
    shared_songs = shared_songs_result.scalars().all()

    return {
        "user": {
            "email": user.email,
            "name": user.name,
            "profile_image_url": user.profile_image_url,
            "createdAt": user.createdAt
        },
        "shared_songs": [
            {
                "title": song.title,
                "artist": song.artist,
                "album": song.album,
                "spotify_url": song.spotify_url,
                "sharedAt": song.sharedAt
            } for song in shared_songs
        ]
    }

@router.put("/profile/{user_id}")
async def update_user_profile_endpoint(
    user_id: int, 
    user_update: UserUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # 현재 사용자가 요청한 user_id와 동일한지 확인
    if current_user.userId != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this profile")

    user = await update_user_profile(db, user_id, user_update)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "Profile updated successfully", "user": user}

@router.get("/profile/{user_id}/following", response_model=List[UserResponse])
async def get_following_list(user_id: int, db: AsyncSession = Depends(get_db)):
    following_result = await db.execute(select(User).join(Follow, Follow.following_id == User.userId).where(Follow.follower_id == user_id))
    following_users = following_result.scalars().all()

    if not following_users:
        raise HTTPException(status_code=404, detail="No following users found")

    return following_users

@router.get("/profile/{user_id}/followers", response_model=List[UserResponse])
async def get_followers_list(user_id: int, db: AsyncSession = Depends(get_db)):
    followers_result = await db.execute(select(User).join(Follow, Follow.follower_id == User.userId).where(Follow.following_id == user_id))
    followers = followers_result.scalars().all()

    if not followers:
        raise HTTPException(status_code=404, detail="No followers found")

    return followers

@router.get("/search", response_model=List[UserResponse])
async def search_user(name: str, db: AsyncSession = Depends(get_db)):
    users = await search_user_by_name(db, name)
    if not users:
        raise HTTPException(status_code=404, detail="No users found with the given name")
    return users


@router.post("/{user_id}/follow")
async def follow_user(user_id: int, request: FollowRequest, db: AsyncSession = Depends(get_db)):
    follower_id = request.follower_id

    if user_id == follower_id:
        raise HTTPException(status_code=400, detail="You cannot follow yourself.")
    
    follow = await add_follow(db, follower_id=follower_id, following_id=user_id)
    
    return {"message": "Followed successfully", "follow": follow}