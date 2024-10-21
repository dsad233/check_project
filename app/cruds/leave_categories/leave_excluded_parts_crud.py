import logging
from datetime import datetime
from typing import List
from fastapi import Depends
from sqlalchemy import func, select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.common.dto.search_dto import BaseSearchDto
from app.models.branches.leave_excluded_parts_model import LeaveExcludedPart
from app.exceptions.exceptions import NotFoundError, BadRequestError

logger = logging.getLogger(__name__)

async def find_all_by_leave_category_id(
    *, session: AsyncSession, leave_category_id: int
) -> List[LeaveExcludedPart]:
    
    stmt = select(LeaveExcludedPart).where(LeaveExcludedPart.leave_category_id == leave_category_id)
    result = await session.execute(stmt)
    return result.scalars().all()


async def create_all_part_id(
    *, session: AsyncSession, leave_category_id: int, part_ids: List[int]
) -> None:
    
    if not part_ids:
        return

    # 벌크 삽입 사용
    insert_stmt = insert(LeaveExcludedPart).values([
        {"leave_category_id": leave_category_id, "part_id": part_id}
        for part_id in part_ids
    ])
    await session.execute(insert_stmt)
    await session.commit()


async def delete_all_part_id(
    *, session: AsyncSession, leave_category_id: int, part_ids: List[int]
) -> None:

    if not part_ids:
        return

    # 벌크 삭제 사용
    delete_stmt = delete(LeaveExcludedPart).where(
        (LeaveExcludedPart.leave_category_id == leave_category_id) & 
        (LeaveExcludedPart.part_id.in_(part_ids))
    )
    await session.execute(delete_stmt)
    await session.commit()
