# src/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config.settings import DATABASE_URL

DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Async engine 생성
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
Base = declarative_base()

# initialize database
async def init_db():
    # run_sync를 사용하여 동기 작업을 비동기 환경에서 실행
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# get_db 함수 추가
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            #await session.close()
            pass