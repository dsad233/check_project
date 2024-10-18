from fastapi import HTTPException
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import AsyncAdaptedQueuePool
from app.core.config import settings
from alembic.config import Config
from alembic import command

meta = MetaData()
engine = create_async_engine(settings.DATABASE_URL,
    echo=False, 
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    poolclass=AsyncAdaptedQueuePool,
    connect_args={
        "charset": "utf8mb4",
        "connect_timeout": 60
    },
    # 추가 설정
    isolation_level="READ COMMITTED",  # 격리 수준 설정
    pool_use_lifo=True,  # LIFO 방식으로 연결 재사용 (성능 향상 가능)
    pool_reset_on_return="rollback",  # 연결 반환 시 롤백 수행
    echo_pool=False
    )


async_session = async_sessionmaker(
    engine, 
    autoflush=False, 
    autocommit=False, 
    class_=AsyncSession
)

Base = declarative_base()

async def get_db():
    db = async_session()
    try:
        yield db
    except Exception as err:
        await db.rollback()
        print(f"Database error: {err}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    finally:
        await db.close()

# Alembic 설정 및 마이그레이션 실행 함수
def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

# FastAPI 애플리케이션 시작 시 실행될 함수
async def startup_event():
    # 동기 함수인 run_migrations를 비동기 컨텍스트에서 실행
    import asyncio
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, run_migrations)
