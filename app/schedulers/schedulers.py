import pytz
from datetime import datetime, timedelta
from sqlalchemy import text
from app.models.db_monitor.connection_logs import ConnectionLogs
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import delete
from app.service import branch_service
from app.core.database import async_session


scheduler = AsyncIOScheduler()


@scheduler.scheduled_job('interval', seconds=300)
async def collect_connection_data():
    async with async_session() as session:
        async with session.begin():
            try:
                # 현재 연결 수 조회
                result = await session.execute(
                    text("SHOW STATUS LIKE 'Threads_connected'")
                )
                count = result.fetchone()
                if count is None:
                    print("No connection count found")
                    return
                        
                current_count = int(count[1])
                kst = pytz.timezone('Asia/Seoul')
                current_time = datetime.now(kst)

                # DB에 저장
                new_log = ConnectionLogs(
                        connection_count=current_count,
                        created_at=current_time
                )
                session.add(new_log)

                # 3일 이전 데이터 삭제
                three_days_ago = current_time - timedelta(days=3)
                delete_stmt = delete(ConnectionLogs).where(ConnectionLogs.created_at < three_days_ago)
                await session.execute(delete_stmt)
                
                await session.commit()
                print(f"[{current_time}] Collected connection count: {current_count}")

            except Exception as e:
                print(f"Error collecting connection data: {str(e)}")
                await session.rollback()


@scheduler.scheduled_job('cron', hour=0, minute=1)
async def auto_grant_leave_days():
    async with async_session() as session:
        async with session.begin():
            await branch_service.auto_annual_leave_grant_scheduling(session=session)
