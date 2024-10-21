import logging
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.exceptions.exceptions import BadRequestError, NotFoundError
from app.models.branches.branches_model import (
    Branches
)

logger = logging.getLogger(__name__)


async def create(
    *, session: AsyncSession, branch_create: Branches
) -> Branches:
            
    # 이름 중복 확인
    stmt = select(Branches).where(Branches.name == branch_create.name)
    result = await session.execute(stmt)
    existing_branch = result.scalar_one_or_none()

    if existing_branch:
        raise BadRequestError(f"지점 이름 '{branch_create.name}'은(는) 이미 존재합니다.")

    session.add(branch_create)
    await session.commit()
    await session.refresh(branch_create)
    return branch_create


async def find_all_by_limit(
    *, session: AsyncSession, offset: int = 0, limit: int = 10
) -> list[Branches]:

    statement = (
        select(Branches).filter(Branches.deleted_yn == "N").offset(offset).limit(limit)
    )
    result = await session.execute(statement)
    return result.scalars().all()

async def find_all(
    *, session: AsyncSession
) -> list[Branches]:

    statement = (
        select(Branches).where(Branches.deleted_yn == "N")
    )
    result = await session.execute(statement)
    return result.scalars().all()


async def find_deleted_all(
    *, session: AsyncSession, offset: int = 0, limit: int = 10
) -> list[Branches]:

    statement = (
        select(Branches).filter(Branches.deleted_yn == "Y").offset(offset).limit(limit)
    )
    result = await session.execute(statement)
    return result.scalars().all()


async def count_all(*, session: AsyncSession) -> int:

    statement = select(func.count()).select_from(Branches)
    result = await session.execute(statement)
    return result.scalar_one()


async def find_by_id(
    *, session: AsyncSession, branch_id: int
) -> Optional[Branches]:
    
    statement = select(Branches).filter(Branches.id == branch_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def delete(*, session: AsyncSession, branch_id: int) -> None:

    branch = await find_by_id(session=session, branch_id=branch_id)
    if branch is None:
        raise NotFoundError(f"{branch_id}번 지점을 찾을 수 없습니다.")
    
    branch.deleted_yn = "Y"
    branch.updated_at = datetime.now()  # 업데이트 시간도 함께 변경

    await session.commit()
    return

async def revive(*, session: AsyncSession, branch_id: int) -> None:

    branch = await find_by_id(session=session, branch_id=branch_id)
    if branch is None:
        raise NotFoundError(f"{branch_id}번 지점을 찾을 수 없습니다.")
    
    branch.deleted_yn = "N"
    branch.updated_at = datetime.now()
    await session.commit()
    return

async def count_deleted_all(*, session: AsyncSession) -> int:

    statement = select(func.count()).select_from(Branches).where(Branches.deleted_yn == "Y")
    result = await session.execute(statement)
    return result.scalar_one()
