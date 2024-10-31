import logging
from datetime import datetime
from sqlalchemy import func, select, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from sqlalchemy.orm import selectinload
from app.exceptions.exceptions import BadRequestError, NotFoundError
from app.models.branches.branches_model import Branches
from app.common.dto.search_dto import BaseSearchDto


logger = logging.getLogger(__name__)


async def create(
    *, session: AsyncSession, request: Branches
) -> Branches:
            
    # 이름 중복 확인
    stmt = select(Branches).where(Branches.name == request.name)
    result = await session.execute(stmt)
    existing_branch = result.scalar_one_or_none()

    if existing_branch:
        raise BadRequestError(f"지점 이름 '{request.name}'은(는) 이미 존재합니다.")

    session.add(request)
    await session.commit()
    await session.flush()
    await session.refresh(request)
    return request


async def find_all_by_limit(
    *, session: AsyncSession, request: BaseSearchDto
) -> list[Branches]:

    statement = (
        select(Branches).filter(Branches.deleted_yn == "N").offset(request.offset).limit(request.record_size)
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
    *, session: AsyncSession, request: BaseSearchDto
) -> list[Branches]:

    statement = (
        select(Branches).filter(Branches.deleted_yn == "Y").offset(request.offset).limit(request.record_size)
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


async def find_by_id_with_policies(
    *, session: AsyncSession, branch_id: int
) -> Optional[Branches]:
    stmt = select(Branches).options(
        selectinload(Branches.overtime_policies),
        selectinload(Branches.holiday_work_policies),
        selectinload(Branches.auto_overtime_policies),
        selectinload(Branches.account_based_annual_leave_grant),
        selectinload(Branches.entry_date_based_annual_leave_grant),
        selectinload(Branches.condition_based_annual_leave_grant),
        selectinload(Branches.auto_annual_leave_approval),
        selectinload(Branches.work_policies),
        selectinload(Branches.allowance_policies)
        ).where(Branches.id == branch_id).where(Branches.deleted_yn == "N")
    result = await session.execute(stmt)
    branch = result.scalar_one_or_none()
    return branch


async def delete(*, session: AsyncSession, branch_id: int) -> bool:

    await session.execute(
            sa_update(Branches)
            .where(Branches.id == branch_id)
            .values(
                deleted_yn="Y",
                updated_at=datetime.now()
            )
        )
    await session.commit()
    return True

async def revive(*, session: AsyncSession, branch_id: int) -> bool:

    await session.execute(
            sa_update(Branches)
            .where(Branches.id == branch_id)
            .values(
                deleted_yn="N",
                updated_at=datetime.now()
            )
        )
    await session.commit()
    return True

async def count_deleted_all(*, session: AsyncSession) -> int:

    statement = select(func.count()).select_from(Branches).where(Branches.deleted_yn == "Y")
    result = await session.execute(statement)
    return result.scalar_one()

async def update(*, session: AsyncSession, branch_id: int, request: Branches, old: Branches) -> bool:
    # 변경된 필드만 업데이트
    changed_fields = {}
    for column in Branches.__table__.columns:
        if column.name not in ['id', 'created_at', 'updated_at', 'deleted_yn']:
            new_value = getattr(request, column.name)
            if new_value is not None and getattr(old, column.name) != new_value:
                changed_fields[column.name] = new_value

    if changed_fields:
        # 변경된 필드가 있을 경우에만 업데이트 수행
        stmt = sa_update(Branches).where(Branches.id == branch_id).values(**changed_fields)
        await session.execute(stmt)
        old.updated_at = datetime.now()
        await session.commit()
        await session.refresh(old)
    else:
        pass
    
    return True
