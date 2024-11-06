from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db

router = APIRouter()

@router.post("/send")
async def send_notification(db: AsyncSession = Depends(get_db)):
    # 사용자에게 알림 전송 기능
    pass  # 추후 구현 필요

@router.get("/{user_id}")
async def get_notifications(user_id: int, db: AsyncSession = Depends(get_db)):
    # 특정 사용자의 모든 알림 조회
    pass  # 추후 구현 필요