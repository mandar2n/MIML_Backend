# src/routers/auths.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from src.crud import create_user
from src.models import Playlist, User
from src.database import get_db
from src.auth.security import get_password_hash, verify_password
from src.auth.auth import create_access_token
from src.schemas import LoginResponse, RegisterRequest, LoginRequest
from datetime import datetime, timedelta
from src.auth.dependencies import get_current_user

router = APIRouter()

@router.post("/register")
async def register_user(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    async with db.begin():  # 트랜잭션 관리
        # 이메일 중복 체크
        result = await db.execute(select(User).filter(User.email == request.email))
        user = result.scalars().first()  

        if user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # 프로필 이미지 URL 처리: 기본값을 설정하거나 request에서 값을 받음
        profile_image_url = request.profile_image_url if request.profile_image_url else "default_image_url"

        # 새로운 사용자 생성
        new_user = User(
            email=request.email,
            hashed_pw=get_password_hash(request.password),
            name=request.name,
            profile_image_url=profile_image_url,
        )
        db.add(new_user)
        await db.flush()  # 임시로 DB에 반영해 `userId` 생성

        # 마이플레이리스트 생성
        new_playlist = Playlist(
            name="My Playlist",  # 기본 이름
            user_id=new_user.userId,
            playlist_type="my",  # 플레이리스트 타입
            createdAt=datetime.utcnow(),
        )
        db.add(new_playlist)
        
    try:
        # 모든 변경사항 커밋
        await db.commit()

        # 새로 생성한 사용자와 플레이리스트 반영
        await db.refresh(new_user)
        await db.refresh(new_playlist) 
        
    except Exception as e:
        await db.rollback()  
        raise HTTPException(status_code=500, detail=f"Failed to register user: {str(e)}")
    
    return {
        "msg": "User registered successfully", 
        "userId": new_user.userId,
        "playlistId": new_playlist.playlistId  # 마이플레이리스트 ID 반환
    } 

@router.post("/login", response_model=LoginResponse)
async def login_user(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    # 사용자 조회
    result = await db.execute(select(User).filter(User.email == request.email))
    user = result.scalars().first()
    
    if not user or not verify_password(request.password, user.hashed_pw):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # 마이플레이리스트 조회
    result = await db.execute(
        select(Playlist).filter(Playlist.user_id == user.userId, Playlist.playlist_type == "my")
    )
    my_playlist = result.scalars().first()

    if not my_playlist:
        raise HTTPException(status_code=500, detail="My Playlist not found for user")

    # 액세스 토큰 생성
    access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=3000))
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "userId": user.userId,
        "playlistId": my_playlist.playlistId,
    }
    
@router.post("/logout")
async def logout_user(current_user: User = Depends(get_current_user)):
    return {"msg": "User logged out. Please clear the token on the client side."}
