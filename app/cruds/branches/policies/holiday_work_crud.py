import logging
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func, select, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from app.models.branches.holiday_work_policies_model import HolidayWorkPolicies
from app.exceptions.exceptions import NotFoundError, BadRequestError


logger = logging.getLogger(__name__)

async def create(
    *, session: AsyncSession, branch_id: int, holiday_work_policies_create: HolidayWorkPolicies = HolidayWorkPolicies()
) -> None:
    
    if await find_by_branch_id(session=session, branch_id=branch_id) is not None:
        raise BadRequestError(f"{branch_id}번 지점의 휴일 근무 정책이 이미 존재합니다.")
    if holiday_work_policies_create.branch_id is None:
        holiday_work_policies_create.branch_id = branch_id
    session.add(holiday_work_policies_create)
    await session.commit()
    await session.refresh(holiday_work_policies_create)

async def update(
    *, session: AsyncSession, branch_id: int, holiday_work_policies_update: HolidayWorkPolicies
) -> None:
    
    # 기존 정책 조회
    holiday_work_policies = await find_by_branch_id(session=session, branch_id=branch_id)

    if holiday_work_policies is None:
        raise NotFoundError(f"{branch_id}번 지점의 휴일 근무 정책이 존재하지 않습니다.")

    # 변경된 필드만 업데이트
    changed_fields = {}
    for column in HolidayWorkPolicies.__table__.columns:
        if column.name not in ['id', 'branch_id']:
            new_value = getattr(holiday_work_policies_update, column.name)
            if new_value is not None and getattr(holiday_work_policies, column.name) != new_value:
                changed_fields[column.name] = new_value

    if changed_fields:
        # 변경된 필드가 있을 경우에만 업데이트 수행
        stmt = sa_update(HolidayWorkPolicies).where(HolidayWorkPolicies.branch_id == branch_id).values(**changed_fields)
        await session.execute(stmt)
        await session.commit()
        await session.refresh(holiday_work_policies)
    else:
        pass

async def find_by_branch_id(
    *, session: AsyncSession, branch_id: int
) -> Optional[HolidayWorkPolicies]:

    stmt = select(HolidayWorkPolicies).where(HolidayWorkPolicies.branch_id == branch_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
