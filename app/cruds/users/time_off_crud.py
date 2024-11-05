# time_off_crud.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.users.time_off_model import TimeOff
from app.models.users.users_model import Users
from app.schemas.user_management.time_off_schemas import TimeOffListResponse, TimeOffListDto, TimeOffResponseDto
from app.core.database import get_db
from fastapi import Depends
from sqlalchemy.exc import MultipleResultsFound

# 휴직 등록
async def time_off_create(
        *,
        session: AsyncSession,
        time_off_create_request: TimeOff
) -> TimeOff:
    try:
        session.add(time_off_create_request)
        await session.commit()
        await session.refresh(time_off_create_request)
        return time_off_create_request
    
    except Exception as error:
        await session.rollback()
        raise error


# 휴직 데이터 업데이트
async def time_off_update(
        *,
        session: AsyncSession,
        time_off_update_request: TimeOff
) -> TimeOff:
    try:
        stmt = select(TimeOff).where(
            TimeOff.id == time_off_update_request.id,
            TimeOff.deleted_yn == 'N'
        )
        result = await session.execute(stmt)
        existing_time_off = result.scalar_one_or_none()

        if existing_time_off:
            update_data = {}
            for column in TimeOff.__table__.columns:
                if (column.name != 'id' 
                    and hasattr(time_off_update_request, column.name)
                    and getattr(time_off_update_request, column.name) is not None):
                    update_data[column.name] = getattr(time_off_update_request, column.name)
            
            for key, value in update_data.items():
                setattr(existing_time_off, key, value)

            await session.commit()
            await session.refresh(existing_time_off)

        return existing_time_off
    
    except Exception as error:
        await session.rollback()
        raise error


# 휴직 데이터 삭제
async def time_off_delete(
        *,
        session: AsyncSession,
        id: int
) -> bool:
    try:
        # 존재하는지 먼저 확인
        stmt = select(TimeOff).where(
            TimeOff.id == id,
            TimeOff.deleted_yn == 'N'
        )
        result = await session.execute(stmt)
        existing_time_off = result.scalar_one_or_none()

        # 존재한다면 삭제(softdelete)
        if existing_time_off:
            existing_time_off.deleted_yn = 'Y'

            await session.commit()
            return True
        
        return False
    
    except Exception as error:
        await session.rollback()
        raise error

