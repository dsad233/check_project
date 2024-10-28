from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update as sa_update
from datetime import datetime
from app.models.branches.condition_based_annual_leave_grant_model import ConditionBasedAnnualLeaveGrant
from app.exceptions.exceptions import NotFoundError, BadRequestError


async def find_by_id(*, session: AsyncSession, id: int) -> ConditionBasedAnnualLeaveGrant:

    stmt = (
        select(ConditionBasedAnnualLeaveGrant)
        .where(ConditionBasedAnnualLeaveGrant.id == id)
    )
    result = await session.execute(stmt)
    policy = result.scalar_one_or_none()

    return policy

async def find_all_by_branch_id(*, session: AsyncSession, branch_id: int) -> list[ConditionBasedAnnualLeaveGrant]:

    stmt = (
        select(ConditionBasedAnnualLeaveGrant)
        .where(ConditionBasedAnnualLeaveGrant.branch_id == branch_id)
        .where(ConditionBasedAnnualLeaveGrant.deleted_yn == 'N')
    )
    result = await session.execute(stmt)
    policy = result.scalars().all()

    return policy

async def create(*, session: AsyncSession, branch_id: int, condition_based_annual_leave_grant_create: ConditionBasedAnnualLeaveGrant = ConditionBasedAnnualLeaveGrant()) -> ConditionBasedAnnualLeaveGrant:

    if condition_based_annual_leave_grant_create.branch_id is None:
        condition_based_annual_leave_grant_create.branch_id = branch_id
    session.add(condition_based_annual_leave_grant_create)
    await session.commit()
    await session.refresh(condition_based_annual_leave_grant_create)
    return condition_based_annual_leave_grant_create
    
async def update(*, session: AsyncSession, branch_id: int, condition_based_annual_leave_grant_update: ConditionBasedAnnualLeaveGrant) -> ConditionBasedAnnualLeaveGrant:

    # 기존 정책 조회
    condition_based_annual_leave_grant = await find_by_id(session=session, id=condition_based_annual_leave_grant_update.id)

    if condition_based_annual_leave_grant is None:
        raise NotFoundError(f"{branch_id}번 지점의 {condition_based_annual_leave_grant_update.id}번 자동 부여 정책이 존재하지 않습니다.")
    
    # 변경된 필드만 업데이트
    changed_fields = {}
    for column in ConditionBasedAnnualLeaveGrant.__table__.columns:
        if column.name not in ['id', 'branch_id', 'created_at', 'updated_at', 'deleted_yn']:
            new_value = getattr(condition_based_annual_leave_grant_update, column.name)
            if new_value is not None and getattr(condition_based_annual_leave_grant, column.name) != new_value:
                changed_fields[column.name] = new_value

    if changed_fields:
        # 변경된 필드가 있을 경우에만 업데이트 수행
        stmt = sa_update(ConditionBasedAnnualLeaveGrant).where(ConditionBasedAnnualLeaveGrant.id == condition_based_annual_leave_grant_update.id).where(ConditionBasedAnnualLeaveGrant.branch_id == branch_id).values(**changed_fields)
        await session.execute(stmt)
        condition_based_annual_leave_grant.updated_at = datetime.now()
        await session.commit()
        await session.refresh(condition_based_annual_leave_grant)
    else:
        pass

    return condition_based_annual_leave_grant
