from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.common.dto.search_dto import BaseSearchDto
from datetime import datetime
from app.models.branches.leave_categories_model import LeaveCategories, LeaveCreate
from fastapi import Depends

async def create_leave_category(*, session: AsyncSession, leave_create: LeaveCreate) -> LeaveCategories:
    db_obj = LeaveCategories(**leave_create.model_dump())
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj

async def find_leave_category_all(*, session: AsyncSession, branch_id: int, search: BaseSearchDto = Depends()) -> list[LeaveCategories]:
    statement = select(LeaveCategories).filter(LeaveCategories.deleted_yn == "N", LeaveCategories.branch_id == branch_id).offset(search.offset).limit(search.record_size)
    result = await session.execute(statement)
    return result.scalars().all()

async def find_leave_category_by_id(*, session: AsyncSession, branch_id: int, leave_id: int) -> LeaveCategories:
    statement = select(LeaveCategories).filter(LeaveCategories.id == leave_id, LeaveCategories.branch_id == branch_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()

async def count_leave_category_all(*, session: AsyncSession, branch_id: int) -> int:
    statement = select(func.count(LeaveCategories.id)).filter(LeaveCategories.deleted_yn == "N", LeaveCategories.branch_id == branch_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()