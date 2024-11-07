from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from src.models import User
from src.database import get_db
from src.auth.security import get_password_hash, verify_password
from src.auth.auth import create_access_token
from src.schemas import RegisterRequest, LoginRequest
from datetime import timedelta

router = APIRouter()

@router.post("/register")
async def register_user(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.email == request.email))
    user = result.scalars().first()  # Get the first result

    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create a new user
    new_user = User(
        email=request.email,
        hashed_password=get_password_hash(request.password),
        name=request.name
    )
    db.add(new_user)
    await db.commit() 
    await db.refresh(new_user) 

    return {"msg": "User registered successfully"}

@router.post("/login")
async def login_user(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.email == request.email))
    user = result.scalars().first()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=30))
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout_user():
    return {"msg": "User logged out. Please clear the token on the client side."}
