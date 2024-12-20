from datetime import datetime
from typing import Optional
from sqlalchemy import func, select, update as sa_update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.branches.leave_categories_model import LeaveCategory


async def create(
    *, branch_id: int, session: AsyncSession, request: LeaveCategory
) -> LeaveCategory:
    
    session.add(request)
    await session.commit()
    await session.refresh(request)
    return request
    

async def find_by_name_and_branch_id(
    *, session: AsyncSession, branch_id: int, name: str
) -> Optional[LeaveCategory]:

    statement = (
        select(LeaveCategory)
        .where(LeaveCategory.branch_id == branch_id)
        .where(LeaveCategory.name == name)
        .where(LeaveCategory.deleted_yn == "N")
    )
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def find_all_with_excluded_parts(
    *, session: AsyncSession, branch_id: int
) -> list[LeaveCategory]:
    
    stmt = (
        select(LeaveCategory).options(selectinload(LeaveCategory.excluded_parts))
        .where(LeaveCategory.branch_id == branch_id)
        .where(LeaveCategory.deleted_yn == "N")
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def find_all_by_branch_id(
    *, session: AsyncSession, branch_id: int
) -> list[LeaveCategory]:

    statement = (
        select(LeaveCategory)
        .where(LeaveCategory.branch_id == branch_id)
        .where(LeaveCategory.deleted_yn == "N")
    )
    result = await session.execute(statement)
    return result.scalars().all()

async def find_by_id_and_branch_id(
    *, session: AsyncSession, branch_id: int, leave_id: int
) -> LeaveCategory:
    
    stmt = (
        select(LeaveCategory)
        .where(LeaveCategory.branch_id == branch_id)
        .where(LeaveCategory.deleted_yn == 'N')
        .where(LeaveCategory.id == leave_id)
    )
    result = await session.execute(stmt)
    policy = result.scalar_one_or_none()
    
    return policy


async def count_all(*, session: AsyncSession, branch_id: int) -> int:
    
    statement = (
        select(func.count(LeaveCategory.id))
        .where(LeaveCategory.deleted_yn == "N")
        .where(LeaveCategory.branch_id == branch_id)
    )
    result = await session.execute(statement)
    return result.scalar_one_or_none()

async def update(
    *, session: AsyncSession, branch_id: int, leave_category_id: int, request: LeaveCategory, old: LeaveCategory
) -> bool:

    # 변경된 필드만 업데이트
    changed_fields = {}
    for column in LeaveCategory.__table__.columns:
        if column.name not in ['id', 'branch_id', 'created_at', 'updated_at', 'deleted_yn']:
            new_value = getattr(request, column.name)
            if new_value is not None and getattr(old, column.name) != new_value:
                changed_fields[column.name] = new_value

    if changed_fields:
        # 변경된 필드가 있을 경우에만 업데이트 수행
        stmt = sa_update(LeaveCategory).where(LeaveCategory.branch_id == branch_id).where(LeaveCategory.id == leave_category_id).values(**changed_fields)
        await session.execute(stmt)
        old.updated_at = datetime.now()
        await session.commit()
        await session.refresh(old)
    else:
        pass

    return True


async def delete(
    *, session: AsyncSession, branch_id: int, leave_category_id: int
) -> bool:
    
    await session.execute(
            sa_update(LeaveCategory)
            .where(LeaveCategory.id == leave_category_id)
            .values(
                deleted_yn="Y",
                updated_at=datetime.now()
            )
        )
    await session.commit()
    return True
