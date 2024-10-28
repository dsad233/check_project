from typing import Optional

from sqlalchemy import select, Tuple
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.users.users_model import Users
from app.models.users.users_work_contract_model import WorkContract, FixedRestDay


async def find_work_contract_by_user_id(
    *, session: AsyncSession, user_id: int
) -> Optional[WorkContract]:
    stmt = (
        select(WorkContract)
        .options(
            joinedload(WorkContract.user)  # user 정보도 함께 로드
        )
        .where(WorkContract.user_id == user_id)
        .join(
            WorkContract.user,
        )
        .where(
            Users.deleted_yn == "N",
        )
    )
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def find_work_contract_part_timer_by_user_id(
    *, session: AsyncSession, user_id: int
) -> Optional[WorkContract]:
    ...



async def find_user_by_user_id(
    *, session: AsyncSession, user_id: int
) -> Optional[Users]:
    stmt = (
        select(Users)
        .where(Users.id == user_id)
        .where(Users.deleted_yn == "N")
    )
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()

async def create_work_contract_with_rest_days(
   *,
   session: AsyncSession,
   work_contract_dict: dict,
   fixed_rest_days: list[dict]
) -> int:
   try:
       # 1. 근로계약 생성
       work_contract_stmt = insert(WorkContract).values(**work_contract_dict)
       work_contract_result = await session.execute(work_contract_stmt)
       work_contract_id = work_contract_result.lastrowid

       # 2. 고정 휴무일 생성
       if fixed_rest_days:
           rest_days_stmt = insert(FixedRestDay).values([
               {"work_contract_id": work_contract_id, **rest_day}
               for rest_day in fixed_rest_days
           ])
           await session.execute(rest_days_stmt)

       # 3. 모든 작업이 성공하면 커밋
       await session.commit()
       return work_contract_id

   except Exception as e:
       # 4. 실패시 롤백
       await session.rollback()
       raise e