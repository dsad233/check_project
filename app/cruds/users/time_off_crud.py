# time_off_crud.py
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.users.time_off_model import TimeOff
from app.schemas.user_management.time_off_schemas import TimeOffReadAllResponseDto
from app.models.users.users_model import Users
from app.models.branches.branches_model import Branches
from app.models.parts.parts_model import Parts


# 모든 휴직 데이터 조회
async def time_off_read_all(
        *,
        session: AsyncSession,
        branch_name: Optional[str] = None,
        part_name: Optional[str] = None,
        name: Optional[str] = None
) -> List[TimeOffReadAllResponseDto]:
    try:
        stmt = (
            select(
                TimeOff,
                Users.name.label('name'),
                Branches.name.label('branch_name'),
                Parts.name.label('part_name')
            )
            .join(Users, TimeOff.user_id == Users.id)
            .join(Branches, Users.branch_id == Branches.id)
            .join(Parts, Users.part_id == Parts.id)
            .where(TimeOff.deleted_yn == 'N')
        )

        # 필터 조건이 있을 경우 필터링
        if branch_name:
            stmt = stmt.where(Branches.name == branch_name)
        if part_name:
            stmt = stmt.where(Parts.name == part_name)
        if name:
            stmt = stmt.where(Users.name == name)

        # 내림차순 정렬
        stmt = stmt.order_by(TimeOff.created_at.desc())

        # 실행
        result = await session.execute(stmt)
        result_all = result.all()

        # 조회결과가 없다면 빈 리스트 반환
        return [
            TimeOffReadAllResponseDto(
                id = result_one.TimeOff.id,
                user_id = result_one.TimeOff.user_id,
                time_off_type = result_one.TimeOff.time_off_type,
                start_date = result_one.TimeOff.start_date,
                end_date = result_one.TimeOff.end_date,
                description = result_one.TimeOff.description,
                is_paid = result_one.TimeOff.is_paid,
                name = result_one.name,
                branch_name = result_one.branch_name,
                part_name = result_one.part_name,
                created_at = result_one.TimeOff.created_at
            )
            for result_one in result_all
        ]

    except Exception as error:
        await session.rollback()
        raise error


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

