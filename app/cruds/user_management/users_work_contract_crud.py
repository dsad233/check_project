from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.users.users_model import Users
from app.models.users.users_work_contract_model import WorkContract


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