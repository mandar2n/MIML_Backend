import asyncio
from src.database import engine
from src.models import Base

async def reset_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

# 비동기 함수 실행
asyncio.run(reset_database())