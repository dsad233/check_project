from typing import Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update as sa_update
from datetime import datetime
from app.models.branches.condition_based_annual_leave_grant_model import ConditionBasedAnnualLeaveGrant
from app.exceptions.exceptions import NotFoundError, BadRequestError


async def find_by_id(*, session: AsyncSession, branch_id: int, id: int) -> Optional[ConditionBasedAnnualLeaveGrant]:
    stmt = select(ConditionBasedAnnualLeaveGrant).where(ConditionBasedAnnualLeaveGrant.branch_id == branch_id).where(ConditionBasedAnnualLeaveGrant.id == id)
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()

async def find_all_by_branch_id(*, session: AsyncSession, branch_id: int) -> list[ConditionBasedAnnualLeaveGrant]:

    stmt = (
        select(ConditionBasedAnnualLeaveGrant)
        .where(ConditionBasedAnnualLeaveGrant.branch_id == branch_id)
        .where(ConditionBasedAnnualLeaveGrant.deleted_yn == 'N')
    )
    result = await session.execute(stmt)
    policy = result.scalars().all()

    return policy

async def create(*, session: AsyncSession, branch_id: int, request: ConditionBasedAnnualLeaveGrant = ConditionBasedAnnualLeaveGrant()) -> ConditionBasedAnnualLeaveGrant:

    if request.branch_id is None:
        request.branch_id = branch_id
    session.add(request)
    await session.flush()
    await session.refresh(request)
    return request
    
async def update(*, session: AsyncSession, branch_id: int, request: ConditionBasedAnnualLeaveGrant, old: ConditionBasedAnnualLeaveGrant) -> bool:

    # 변경된 필드만 업데이트
    changed_fields = {}
    for column in ConditionBasedAnnualLeaveGrant.__table__.columns:
        if column.name not in ['id', 'branch_id', 'created_at', 'updated_at', 'deleted_yn']:
            new_value = getattr(request, column.name)
            if new_value is not None and getattr(old, column.name) != new_value:
                changed_fields[column.name] = new_value

    if changed_fields:
        # 변경된 필드가 있을 경우에만 업데이트 수행
        stmt = sa_update(ConditionBasedAnnualLeaveGrant).where(ConditionBasedAnnualLeaveGrant.id == old.id).values(**changed_fields)
        await session.execute(stmt)
        old.updated_at = datetime.now()
        await session.flush()
        await session.refresh(old)
    else:
        pass

    return True


async def delete_all_id(
    *, session: AsyncSession, branch_id: int, ids: list[int]
) -> None:

    if not ids:
        return

    # 벌크 삭제 사용
    delete_stmt = delete(ConditionBasedAnnualLeaveGrant).where(
        (ConditionBasedAnnualLeaveGrant.branch_id == branch_id) & 
        (ConditionBasedAnnualLeaveGrant.id.in_(ids))
    )
    await session.execute(delete_stmt)
    await session.commit()