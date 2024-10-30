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
    *, session: AsyncSession, branch_id: int, allowance_policies_create: AllowancePolicies = AllowancePolicies()
) -> None:

    if await find_by_branch_id(session=session, branch_id=branch_id) is not None:
        raise BadRequestError(f"{branch_id}번 지점의 수당 정책이 이미 존재합니다.")
    if allowance_policies_create.branch_id is None:
        allowance_policies_create.branch_id = branch_id
    session.add(allowance_policies_create)
    await session.commit()
    await session.flush()
    await session.refresh(allowance_policies_create)
    
async def update(
    *, session: AsyncSession, branch_id: int, allowance_policies_update: AllowancePolicies
) -> None:
    
    # 기존 정책 조회
    allowance_policies = await find_by_branch_id(session=session, branch_id=branch_id)

    if allowance_policies is None:
        raise NotFoundError(f"{branch_id}번 지점의 수당 정책이 존재하지 않습니다.")
    
    # 변경된 필드만 업데이트
    changed_fields = {}
    for column in AllowancePolicies.__table__.columns:
        if column.name not in ['id', 'branch_id', 'created_at', 'updated_at', 'deleted_yn']:
            new_value = getattr(allowance_policies_update, column.name)
            if new_value is not None and getattr(allowance_policies, column.name) != new_value:
                changed_fields[column.name] = new_value

    if changed_fields:
        # 변경된 필드가 있을 경우에만 업데이트 수행
        stmt = sa_update(AllowancePolicies).where(AllowancePolicies.branch_id == branch_id).values(**changed_fields)
        await session.execute(stmt)
        allowance_policies.updated_at = datetime.now()
        await session.commit()
        await session.refresh(allowance_policies)
    else:
        pass
   

async def find_by_branch_id(
    *, session: AsyncSession, branch_id: int
) -> Optional[AllowancePolicies]:

    stmt = select(AllowancePolicies).where(AllowancePolicies.branch_id == branch_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
