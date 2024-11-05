from fastapi import HTTPException
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import AsyncAdaptedQueuePool
from app.core.config import settings
from alembic.config import Config
from alembic import command

meta = MetaData()
engine = create_async_engine(settings.DATABASE_URL,
    echo=True, 
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=30,
    max_overflow=20,
    pool_timeout=30,
    poolclass=AsyncAdaptedQueuePool,
    connect_args={
        "charset": "utf8mb4",
        "connect_timeout": 60
    }
    )


async_session = async_sessionmaker(
    engine, 
    autoflush=False, 
    autocommit=False,
    expire_on_commit=False,
    class_=AsyncSession
)

class Base(DeclarativeBase):
    pass


async def get_db():
    db = async_session()
    try:
        yield db
    finally:
        await db.commit()
        await db.close()

# Alembic 설정 및 마이그레이션 실행 함수
def run_migrations():
    alembic_cfg = Config("alembic.ini")
    # command.upgrade(alembic_cfg, "head")

# FastAPI 애플리케이션 시작 시 실행될 함수
async def startup_event():
    # 동기 함수인 run_migrations를 비동기 컨텍스트에서 실행
    import asyncio
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, run_migrations)