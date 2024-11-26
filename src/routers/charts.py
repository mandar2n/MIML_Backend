# app/routers/charts.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.crud import get_daily_chart, get_weekly_chart, get_monthly_chart, get_yearly_chart
from src.schemas import ChartResponse  # 추가
from typing import List

router = APIRouter()

@router.get("/daily", response_model=List[ChartResponse])
async def daily_chart(db: AsyncSession = Depends(get_db)):
    chart = await get_daily_chart(db)
    return chart

@router.get("/weekly", response_model=List[ChartResponse])
async def weekly_chart(db: AsyncSession = Depends(get_db)):
    chart = await get_weekly_chart(db)
    return chart

@router.get("/monthly", response_model=List[ChartResponse])
async def monthly_chart(db: AsyncSession = Depends(get_db)):
    chart = await get_monthly_chart(db)
    return chart

@router.get("/yearly", response_model=List[ChartResponse])
async def monthly_chart(db: AsyncSession = Depends(get_db)):
    chart = await get_yearly_chart(db)
    return chart