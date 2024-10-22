import logging
from typing import Optional
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from fastapi import HTTPException
from sqlalchemy import func, select, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.exceptions import NotFoundError, BadRequestError

from app.models.branches.auto_overtime_policies_model import AutoOvertimePolicies

logger = logging.getLogger(__name__)

async def create(
    *, session: AsyncSession, branch_id: int, auto_overtime_policies_create: AutoOvertimePolicies = AutoOvertimePolicies()
) -> None:
    
    if await find_by_branch_id(session=session, branch_id=branch_id) is not None:
        raise BadRequestError(f"{branch_id}번 지점의 자동 초과 근무 정책이 이미 존재합니다.")
    if auto_overtime_policies_create.branch_id is None:
        auto_overtime_policies_create.branch_id = branch_id
    session.add(auto_overtime_policies_create)
    await session.commit()
    await session.refresh(auto_overtime_policies_create)

async def update(
    *, session: AsyncSession, branch_id: int, auto_overtime_policies_update: AutoOvertimePolicies
) -> None:
    
    # 기존 정책 조회
    auto_overtime_policies = await find_by_branch_id(session=session, branch_id=branch_id)

    if auto_overtime_policies is None:
        raise NotFoundError(f"{branch_id}번 지점의 자동 초과 근무 정책이 존재하지 않습니다.")
        
    # 변경된 필드만 업데이트
    changed_fields = {}
    for column in AutoOvertimePolicies.__table__.columns:
        if column.name not in ['id', 'branch_id', 'created_at', 'updated_at', 'deleted_yn']:
            new_value = getattr(auto_overtime_policies_update, column.name)
            if new_value is not None and getattr(auto_overtime_policies, column.name) != new_value:
                changed_fields[column.name] = new_value

    if changed_fields:
        # 변경된 필드가 있을 경우에만 업데이트 수행
        stmt = sa_update(AutoOvertimePolicies).where(AutoOvertimePolicies.branch_id == branch_id).values(**changed_fields)
        await session.execute(stmt)
        auto_overtime_policies.updated_at = datetime.now()
        await session.commit()
        await session.refresh(auto_overtime_policies)
    else:
        pass

async def find_by_branch_id(
    *, session: AsyncSession, branch_id: int
) -> Optional[AutoOvertimePolicies]:

    stmt = select(AutoOvertimePolicies).where(AutoOvertimePolicies.branch_id == branch_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()