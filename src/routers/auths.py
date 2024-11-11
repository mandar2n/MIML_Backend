# src/routers/auths.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from src.crud import create_user
from src.models import User
from src.database import get_db
from src.auth.security import get_password_hash, verify_password
from src.auth.auth import create_access_token
from src.schemas import RegisterRequest, LoginRequest
from datetime import timedelta

router = APIRouter()

@router.post("/register")
async def register_user(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    
    # 이메일 중복 체크
    result = await db.execute(select(User).filter(User.email == request.email))
    user = result.scalars().first()  

    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 프로필 이미지 URL 처리: 기본값을 설정하거나 request에서 값을 받음
    profile_image_url = request.profile_image_url if request.profile_image_url else "default_image_url"

    # 새로운 사용자 생성
    new_user = await create_user(
        db=db,
        email=request.email,
        hashed_password=get_password_hash(request.password),
        name=request.name,
        profile_image_url=profile_image_url
    )
    
    db.add(new_user)

    try:
        await db.commit() 
        await db.refresh(new_user)  
    except Exception as e:
        await db.rollback()  
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"msg": "User registered successfully", "userId": new_user.userId}

@router.post("/login")
async def login_user(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.email == request.email))
    user = result.scalars().first()
    
    if not user or not verify_password(request.password, user.hashed_pw):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=30))
    
    return {"access_token": access_token, "token_type": "bearer", "userId": user.userId}

@router.post("/logout")
async def logout_user():
    return {"msg": "User logged out. Please clear the token on the client side."}
