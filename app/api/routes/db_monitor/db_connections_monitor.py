from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import List
from pydantic import BaseModel
from app.core.database import get_db, async_session
from fastapi.responses import HTMLResponse
from sqlalchemy import text, select, delete
from app.models.db_monitor.connection_logs import ConnectionLogs
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
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
        kst = pytz.timezone('Asia/Seoul')
        current_time = datetime.now(kst)
        
        # 가장 최근 데이터 조회
        query = (
            select(ConnectionLogs)
            .order_by(ConnectionLogs.created_at.desc())
            .limit(1)
        )
        
        result = await db.execute(query)
        latest_log = result.scalar_one_or_none()
        
        if latest_log is None:
            return [{
                "timestamp": current_time,
                "connection_count": 0
            }]
            
        return [{
            "timestamp": latest_log.created_at,
            "connection_count": latest_log.connection_count
        }]
    except Exception as e:
        print(f"Error in get_connections: {str(e)}")
        raise

@router.get("/metrics/connection-history", response_model=List[ConnectionData])
async def get_connection_history(db: AsyncSession = Depends(get_db)):
    try:
        kst = pytz.timezone('Asia/Seoul')
        three_days_ago = datetime.now(kst) - timedelta(days=3)
        
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