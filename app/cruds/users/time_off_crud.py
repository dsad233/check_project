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


# async def time_off_find_by_user_id(
#         *,
#         session: AsyncSession,
#         user_id: int
# ) -> TimeOffGetResponseDto:
    
#     try:
#         # userid를 기준으로, 이미 생성된 휴직 데이터가 있는지 찾는다.
#         stmt = select(TimeOff).where(TimeOff.user_id == user_id).where(TimeOff.deleted_yn == 'N')
#         result = await session.execute(stmt)
#         return result.scalar_one_or_none()
    
#     # 휴직 데이터가 여러 개 있을 경우 예외 처리
#     except MultipleResultsFound:
        
    
    

async def time_off_create(
        *,
        session: AsyncSession,
        time_off_create_request: TimeOff
) -> TimeOff:
    
    session.add(time_off_create_request)
    await session.commit()
    await session.refresh(time_off_create_request)
    return time_off_create_request


async def time_off_update(
        *,
        session: AsyncSession,
        time_off_update_request: TimeOff
) -> TimeOff:
    
    stmt = select(TimeOff).where(
        TimeOff.id == time_off_update_request.id,
        TimeOff.deleted_yn == 'N'
    )
    result = await session.execute(stmt)
    existing_time_off = result.scalar_one_or_none()

    if existing_time_off:
        # request data를 딕셔너리 형태로 가져와 순회
        for key, value in time_off_update_request.__dict__.items():
            if hasattr(existing_time_off, key) and key != 'id':
                setattr(existing_time_off, key, value)

        await session.commit()
        await session.refresh(existing_time_off)

    # 객체 리턴 or None
    return existing_time_off




# async def time_off_list(
#         *,
#         session: AsyncSession,
#         user_id: int
# ) -> TimeOffListResponse:
#     query = (
#         select(TimeOff)
#         .options(
#             joinedload(TimeOff.user)
#             .joinedload(Users.branch)  # branch 관계 로드
#             .joinedload(Users.part)  # part 관계 로드
#         )
#         .where(TimeOff.user_id == user_id)
#     )

#     result = await session.execute(query)
#     time_offs = result.unique().scalars().all()

#     time_off_list = [
#         TimeOffListDto(
#             id=time_off.id,
#             branch_name=time_off.user.branch.name,
#             part_name=time_off.user.part.name,
#             created_at=time_off.created_at.date(),
#             time_off_type=time_off.time_off_type,
#             start_date=time_off.start_date,
#             end_date=time_off.end_date,
#             description=time_off.description
#         ) for time_off in time_offs
#     ]

#     return TimeOffListResponse(time_offs=time_off_list)