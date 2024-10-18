from datetime import datetime
from typing import List
from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dto.search_dto import BaseSearchDto
from app.models.branches.leave_excluded_parts_model import LeaveExcludedPart, LeaveExcludedPartResponse


async def create(
    *, session: AsyncSession, leave_category_id: int, part_id: int
) -> int:
    db_obj = LeaveExcludedPart(leave_category_id=leave_category_id, part_id=part_id)
    if await get_by_part_id_and_leave_category_id(session=session, leave_category_id=leave_category_id, part_id=part_id):
        raise ValueError(f"LeaveExcludedPart with part_id {part_id} and leave_category_id {leave_category_id} already exists")
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj.id

async def get_by_part_id_and_leave_category_id(
    *, session: AsyncSession, leave_category_id: int, part_id: int
) -> LeaveExcludedPart:
    stmt = select(LeaveExcludedPart).where(LeaveExcludedPart.leave_category_id == leave_category_id, LeaveExcludedPart.part_id == part_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def get_all_by_leave_category_id(
    *, session: AsyncSession, leave_category_id: int
) -> List[LeaveExcludedPart]:
    stmt = select(LeaveExcludedPart).where(LeaveExcludedPart.leave_category_id == leave_category_id)
    result = await session.execute(stmt)
    return result.scalars().all()

async def delete(
    *, session: AsyncSession, leave_excluded_part_id: int
) -> int:
    stmt = select(LeaveExcludedPart).where(LeaveExcludedPart.id == leave_excluded_part_id)
    result = await session.execute(stmt)
    leave_excluded_part = result.scalar_one_or_none()
    if leave_excluded_part is None:
        raise ValueError(f"LeaveExcludedPart with id {leave_excluded_part_id} not found")
    await session.delete(leave_excluded_part)
    await session.commit()
    return leave_excluded_part.id

async def delete_by_part_id(
    *, session: AsyncSession, leave_category_id: int, part_id: int
) -> int:
    stmt = select(LeaveExcludedPart).where(LeaveExcludedPart.leave_category_id == leave_category_id, LeaveExcludedPart.part_id == part_id)
    result = await session.execute(stmt)
    leave_excluded_part = result.scalar_one_or_none()
    if leave_excluded_part is None:
        raise ValueError(f"LeaveExcludedPart with part_id {part_id} and leave_category_id {leave_category_id} not found")
    await session.delete(leave_excluded_part)
    await session.commit()