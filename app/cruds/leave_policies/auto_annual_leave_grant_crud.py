import logging
from typing import List, Optional
from fastapi import Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, select, exists, update
from sqlalchemy import update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound
from app.common.dto.search_dto import BaseSearchDto
from app.models.branches.auto_annual_leave_grant_model import AutoAnnualLeaveGrant
from app.exceptions.exceptions import NotFoundError, BadRequestError

logger = logging.getLogger(__name__)

async def find_by_branch_id(*, session: AsyncSession, branch_id: int) -> Optional[AutoAnnualLeaveGrant]:

    stmt = (
        select(AutoAnnualLeaveGrant)
        .where(AutoAnnualLeaveGrant.branch_id == branch_id)
        .where(AutoAnnualLeaveGrant.deleted_yn == 'N')
    )
    result = await session.execute(stmt)
    policy = result.scalar_one_or_none()

    return policy

async def create(*, session: AsyncSession, branch_id: int, auto_annual_leave_grant_create: AutoAnnualLeaveGrant = AutoAnnualLeaveGrant()) -> AutoAnnualLeaveGrant:

    if await find_by_branch_id(session=session, branch_id=branch_id) is not None:
        raise BadRequestError(f"{branch_id}번 지점의 자동 부여 정책이 이미 존재합니다.")
    if auto_annual_leave_grant_create.branch_id is None:
        auto_annual_leave_grant_create.branch_id = branch_id
    session.add(auto_annual_leave_grant_create)
    await session.commit()
    await session.refresh(auto_annual_leave_grant_create)
    return auto_annual_leave_grant_create
    
async def update(*, session: AsyncSession, branch_id: int, auto_annual_leave_grant_update: AutoAnnualLeaveGrant) -> AutoAnnualLeaveGrant:

    # 기존 정책 조회
    auto_annual_leave_grant = await find_by_branch_id(session=session, branch_id=branch_id)

    if auto_annual_leave_grant is None:
        raise NotFoundError(f"{branch_id}번 지점의 자동 부여 정책이 존재하지 않습니다.")
    
    # 변경된 필드만 업데이트
    changed_fields = {}
    for column in AutoAnnualLeaveGrant.__table__.columns:
        if column.name not in ['id', 'branch_id']:
            new_value = getattr(auto_annual_leave_grant_update, column.name)
            if new_value is not None and getattr(auto_annual_leave_grant, column.name) != new_value:
                changed_fields[column.name] = new_value

    if changed_fields:
        # 변경된 필드가 있을 경우에만 업데이트 수행
        stmt = sa_update(AutoAnnualLeaveGrant).where(AutoAnnualLeaveGrant.branch_id == branch_id).values(**changed_fields)
        await session.execute(stmt)
        await session.commit()
        await session.refresh(auto_annual_leave_grant)
    else:
        pass

    return auto_annual_leave_grant