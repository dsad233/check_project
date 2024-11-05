import pytest
from app.main import app
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.database import Base
from fastapi.testclient import TestClient
from app.middleware.jwt.jwtService import JWTService
from app.middleware.jwt.jwtEncoder import JWTEncoder
from app.middleware.jwt.jwtDecoder import JWTDecoder
from sqlalchemy.pool import NullPool


@pytest.fixture(scope="function")
async def db():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=NullPool,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args={"check_same_thread": False}
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        engine, 
        autoflush=False, 
        autocommit=False,
        expire_on_commit=False,
        class_=AsyncSession
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
def client():

    return TestClient(app)


@pytest.fixture(scope="session")
def access_token():
    jwt_service = JWTService(JWTEncoder(), JWTDecoder())

    return jwt_service._create_token(data={"id": "1"})

    