from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.schemas import UserCreate, UserResponse
from src.crud import create_user, get_user_by_email

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

@router.put("/profile/{user_id}")
async def update_profile(user_id: int, user: UserCreate, db: AsyncSession = Depends(get_db)):
    # 사용자 프로필 수정 기능 추가
    pass  # 추후 구현 필요

@router.get("/search")
async def search_user(name: str, db: AsyncSession = Depends(get_db)):
    # 사용자 검색 기능 추가
    pass  # 추후 구현 필요

@router.post("/{user_id}/follow")
async def follow_user(user_id: int, db: AsyncSession = Depends(get_db)):
    # 특정 유저 팔로우 기능 추가
    pass  # 추후 구현 필요