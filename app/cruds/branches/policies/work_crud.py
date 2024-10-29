import logging
from datetime import datetime
from typing import Optional
from fastapi import HTTPException
from sqlalchemy import func, select, update
from sqlalchemy import update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from app.models.branches.work_policies_model import WorkPolicies
from app.exceptions.exceptions import BadRequestError, NotFoundError

logger = logging.getLogger(__name__)

async def create(
    *, session: AsyncSession, branch_id: int, work_policies_create: WorkPolicies = WorkPolicies()
) -> WorkPolicies:

    if await find_by_branch_id(session=session, branch_id=branch_id) is not None:
        raise BadRequestError(f"{branch_id}번 지점의 근무 정책이 이미 존재합니다.")
    if work_policies_create.branch_id is None:
        work_policies_create.branch_id = branch_id
    session.add(work_policies_create)
    await session.commit()
    await session.flush()
    await session.refresh(work_policies_create)
    return work_policies_create

async def update(
    *, session: AsyncSession, branch_id: int, work_policies_update: WorkPolicies
) -> None:

    # 기존 정책 조회
    work_policies = await find_by_branch_id(session=session, branch_id=branch_id)

    if work_policies is None:
        raise NotFoundError(f"{branch_id}번 지점의 근무 정책이 존재하지 않습니다.")
    
    # 변경된 필드만 업데이트
    changed_fields = {}
    for column in WorkPolicies.__table__.columns:
        if column.name not in ['id', 'branch_id', 'created_at', 'updated_at', 'deleted_yn']:
            new_value = getattr(work_policies_update, column.name)
            if new_value is not None and getattr(work_policies, column.name) != new_value:
                changed_fields[column.name] = new_value

    if changed_fields:
        # 변경된 필드가 있을 경우에만 업데이트 수행
        stmt = sa_update(WorkPolicies).where(WorkPolicies.branch_id == branch_id).values(**changed_fields)
        await session.execute(stmt)
        work_policies.updated_at = datetime.now()
        await session.commit()
        await session.refresh(work_policies)
    else:
        pass



async def find_by_branch_id(
    *, session: AsyncSession, branch_id: int
) -> Optional[WorkPolicies]:

    stmt = select(WorkPolicies).where(WorkPolicies.branch_id == branch_id)
    result = await session.execute(stmt)
    db_obj = result.scalar_one_or_none()
    return db_obj

