import logging
from typing import Optional
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import func, select, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from app.models.branches.holiday_work_policies_model import HolidayWorkPolicies
from app.exceptions.exceptions import NotFoundError, BadRequestError


logger = logging.getLogger(__name__)

async def create(
    *, session: AsyncSession, branch_id: int, request: HolidayWorkPolicies = HolidayWorkPolicies()
) -> HolidayWorkPolicies:
    
    if request.branch_id is None:
        request.branch_id = branch_id
    session.add(request)
    await session.flush()
    await session.refresh(request)
    return request


async def update(
    *, session: AsyncSession, branch_id: int, request: HolidayWorkPolicies, old: HolidayWorkPolicies
) -> bool:

    # 변경된 필드만 업데이트
    changed_fields = {}
    for column in HolidayWorkPolicies.__table__.columns:
        if column.name not in ['id', 'branch_id', 'created_at', 'updated_at', 'deleted_yn']:
            new_value = getattr(request, column.name)
            if new_value is not None and getattr(old, column.name) != new_value:
                changed_fields[column.name] = new_value

    if changed_fields:
        # 변경된 필드가 있을 경우에만 업데이트 수행
        stmt = sa_update(HolidayWorkPolicies).where(HolidayWorkPolicies.branch_id == branch_id).values(**changed_fields)
        await session.execute(stmt)
        old.updated_at = datetime.now()
        await session.flush()
        await session.refresh(old)
    else:
        pass

    return True

async def find_by_branch_id(
    *, session: AsyncSession, branch_id: int
) -> Optional[HolidayWorkPolicies]:

    stmt = select(HolidayWorkPolicies).where(HolidayWorkPolicies.branch_id == branch_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
