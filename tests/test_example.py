import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient
from sqlalchemy import select


def test_health_check(client: TestClient, access_token: str):
   response = client.get("/healthcheck")  # health check endpoint
   assert response.status_code == 200
   assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_db_connection(db: AsyncSession):
   # DB가 연결되어 있는지 확인
   await db.execute(select(1))
   assert True