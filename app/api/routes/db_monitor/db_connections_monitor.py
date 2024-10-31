from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import List
from pydantic import BaseModel
from app.core.database import get_db
from fastapi.responses import HTMLResponse
from sqlalchemy import text, select, delete
from app.models.db_monitor.connection_logs import ConnectionLogs
import os
import pytz

router = APIRouter()

current_dir = os.path.dirname(os.path.abspath(__file__))

class ConnectionData(BaseModel):
    timestamp: datetime
    connection_count: int

@router.get("/metrics/connections", response_model=List[ConnectionData])
async def get_connections(db: AsyncSession = Depends(get_db)):
    try:
        # 현재 연결 수 조회
        result = await db.execute(
            text("SHOW STATUS LIKE 'Threads_connected'")
        )
        count = result.fetchone()
        if count is None:
            print("No connection count found")
            return [{
                "timestamp": datetime.now(),
                "connection_count": 0
            }]
        current_count = int(count[1]) if count else 0
        kst = pytz.timezone('Asia/Seoul')
        current_time = datetime.now(kst)

        # DB에 저장
        new_log = ConnectionLogs(
            connection_count=current_count,
            created_at=current_time
        )
        db.add(new_log)

        # 3일 이전 데이터 삭제
        three_days_ago = current_time - timedelta(days=3)
        delete_stmt = delete(ConnectionLogs).where(ConnectionLogs.created_at < three_days_ago)
        await db.execute(delete_stmt)
        
        await db.commit()

        return [{
            "timestamp": current_time,
            "connection_count": current_count
        }]
    except Exception as e:
        print(f"Error in get_connections: {str(e)}")
        await db.rollback()
        raise

@router.get("/metrics/connection-history", response_model=List[ConnectionData])
async def get_connection_history(db: AsyncSession = Depends(get_db)):
    try:
        # 최근 3일간의 데이터 조회
        kst = pytz.timezone('Asia/Seoul')
        three_days_ago = datetime.now(kst) - timedelta(days=3)  # KST 적용
        
        query = (
            select(ConnectionLogs)
            .where(ConnectionLogs.created_at >= three_days_ago)
            .order_by(ConnectionLogs.created_at.asc())
        )
        
        result = await db.execute(query)
        logs = result.scalars().all()
        
        return [
            {
                "timestamp": log.created_at,
                "connection_count": log.connection_count
            }
            for log in logs
        ]
    except Exception as e:
        print(f"Error in get_connection_history: {str(e)}")
        raise

@router.get("/metrics/max-connections")
async def get_max_connections(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            text("SHOW VARIABLES LIKE 'max_connections'")
        )
        max_conn = result.fetchone()
        if max_conn is None:
            print("No max connections value found")
            return {"max_connections": 0}
        return {
            "max_connections": int(max_conn[1])
        }
    except Exception as e:
        print(f"Error in get_max_connections: {str(e)}")
        raise

@router.get("/monitor", response_class=HTMLResponse)
async def get_monitor_page():
    html_path = os.path.join(current_dir, "db_connections_monitor.html")
    with open(html_path, "r", encoding='utf-8') as f:
        return HTMLResponse(content=f.read())