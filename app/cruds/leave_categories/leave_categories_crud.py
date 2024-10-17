from datetime import datetime

from fastapi import Depends
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dto.search_dto import BaseSearchDto
from app.models.branches.leave_categories_model import LeaveCategories, LeaveCategoryCreate, LeaveCategoryUpdate, LeaveCategoryResponse


async def create_leave_category(
    *, branch_id: int, session: AsyncSession, leave_category_create: LeaveCategoryCreate
) -> int:
    db_obj = LeaveCategories(branch_id=branch_id, **leave_category_create.model_dump())
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj.id


async def find_leave_category_all(
    *, session: AsyncSession, branch_id: int
) -> list[LeaveCategories]:
    statement = (
        select(LeaveCategories).where(LeaveCategories.branch_id == branch_id).where(LeaveCategories.deleted_yn == "N")
    )
    result = await session.execute(statement)
    return result.scalars().all()


async def find_leave_category_by_id(
    *, session: AsyncSession, branch_id: int, leave_id: int
) -> LeaveCategories:
    statement = select(LeaveCategories).filter(
        LeaveCategories.id == leave_id, LeaveCategories.branch_id == branch_id
    )
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def count_leave_category_all(*, session: AsyncSession, branch_id: int) -> int:
    statement = select(func.count(LeaveCategories.id)).filter(
        LeaveCategories.deleted_yn == "N", LeaveCategories.branch_id == branch_id
    )
    result = await session.execute(statement)
    return result.scalar_one_or_none()

async def update_leave_category(
    *, session: AsyncSession, branch_id: int, leave_category_id: int, leave_category_update: LeaveCategoryUpdate
) -> None:

    stmt = select(LeaveCategories).where(LeaveCategories.id == leave_category_id)
    result = await session.execute(stmt)
    db_obj = result.scalar_one_or_none()
    if db_obj is None:
        raise ValueError(f"Leave category with id {leave_category_id} not found")
    
    update_data = leave_category_update.model_dump(exclude_unset=True)

    update_stmt = (
        update(LeaveCategories)
        .where(LeaveCategories.id == leave_category_id)
        .values(**update_data)
    )
    await session.execute(update_stmt)
    await session.commit()
    return


async def delete_leave_category(
    *, session: AsyncSession, branch_id: int, leave_category_id: int
) -> None:
    stmt = select(LeaveCategories).where(LeaveCategories.id == leave_category_id, LeaveCategories.branch_id == branch_id)
    result = await session.execute(stmt)
    leave_category = result.scalar_one_or_none()
    if leave_category is None:
        raise ValueError(f"Leave category with id {leave_category_id} not found")
    
    leave_category.deleted_yn = "Y"
    leave_category.updated_at = datetime.now()
    await session.commit()
    return