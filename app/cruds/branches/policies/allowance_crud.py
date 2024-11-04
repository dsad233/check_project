import logging
from datetime import datetime
from typing import Optional
from fastapi import HTTPException
from sqlalchemy import func, select, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.exceptions import NotFoundError, BadRequestError

from app.models.branches.allowance_policies_model import AllowancePolicies

logger = logging.getLogger(__name__)

async def create(
    *, session: AsyncSession, branch_id: int, request: AllowancePolicies = AllowancePolicies()
) -> AllowancePolicies:
    
    if request.branch_id is None:
        request.branch_id = branch_id
    session.add(request)
    await session.flush()
    await session.refresh(request)
    return request


async def update(
    *, session: AsyncSession, branch_id: int, request: AllowancePolicies, old: AllowancePolicies
) -> bool:
    
    # 변경된 필드만 업데이트
    changed_fields = {}
    for column in AllowancePolicies.__table__.columns:
        if column.name not in ['id', 'branch_id', 'created_at', 'updated_at', 'deleted_yn']:
            new_value = getattr(request, column.name)
            if new_value is not None and getattr(old, column.name) != new_value:
                changed_fields[column.name] = new_value

    if changed_fields:
        # 변경된 필드가 있을 경우에만 업데이트 수행
        stmt = sa_update(AllowancePolicies).where(AllowancePolicies.branch_id == branch_id).values(**changed_fields)
        await session.execute(stmt)
        old.updated_at = datetime.now()
        await session.flush()
        await session.refresh(old)
    else:
        pass

    return True
   

async def find_by_branch_id(
    *, session: AsyncSession, branch_id: int
) -> Optional[AllowancePolicies]:

    stmt = select(AllowancePolicies).where(AllowancePolicies.branch_id == branch_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
