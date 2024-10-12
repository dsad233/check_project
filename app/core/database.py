from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings

meta = MetaData()
engine = create_async_engine(settings.DATABASE_URL, echo=True)
async_session = async_sessionmaker(
    engine, autoflush=False, autocommit=False, class_=AsyncSession
)

Base = declarative_base()


async def get_db():
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)

    db = async_session()
    try:
        yield db
    finally:
        await db.close()
