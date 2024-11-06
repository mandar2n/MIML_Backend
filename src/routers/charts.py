from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db

router = APIRouter()

@router.get("/")
async def get_charts(db: AsyncSession = Depends(get_db)):
    # 하루, 월, 연간 차트 조회
    pass  # 추후 구현 필요