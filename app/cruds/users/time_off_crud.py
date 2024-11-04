# time_off_crud.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.users.time_off_model import TimeOff
from app.models.users.users_model import Users
from app.schemas.user_management.time_off_schemas import TimeOffListResponse, TimeOffListDto, TimeOffGetResponseDto
from app.core.database import get_db
from fastapi import Depends


async def time_off_find_by_user_id(
        *,
        session: AsyncSession,
        user_id: int
) -> TimeOffGetResponseDto:
    
    # userid를 기준으로, 이미 생성된 휴직 데이터가 있는지 찾는다.
    

async def time_off_create(
        *,
        session: AsyncSession,
        time_off_create_request: TimeOff
) -> TimeOff:
    
    session.add(time_off_create_request)
    await session.commit()
    await session.refresh(time_off_create_request)
    return time_off_create_request
    


async def time_off_list(
        *,
        session: AsyncSession,
        user_id: int
) -> TimeOffListResponse:
    query = (
        select(TimeOff)
        .options(
            joinedload(TimeOff.user)
            .joinedload(Users.branch)  # branch 관계 로드
            .joinedload(Users.part)  # part 관계 로드
        )
        .where(TimeOff.user_id == user_id)
    )

    result = await session.execute(query)
    time_offs = result.unique().scalars().all()

    time_off_list = [
        TimeOffListDto(
            id=time_off.id,
            branch_name=time_off.user.branch.name,
            part_name=time_off.user.part.name,
            created_at=time_off.created_at.date(),
            time_off_type=time_off.time_off_type,
            start_date=time_off.start_date,
            end_date=time_off.end_date,
            description=time_off.description
        ) for time_off in time_offs
    ]

    return TimeOffListResponse(time_offs=time_off_list)