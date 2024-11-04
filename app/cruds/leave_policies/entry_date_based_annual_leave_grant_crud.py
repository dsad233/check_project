from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update as sa_update
from datetime import datetime
from app.models.branches.entry_date_based_annual_leave_grant_model import EntryDateBasedAnnualLeaveGrant
from app.exceptions.exceptions import NotFoundError, BadRequestError


async def find_by_branch_id(*, session: AsyncSession, branch_id: int) -> Optional[EntryDateBasedAnnualLeaveGrant]:

    stmt = (
        select(EntryDateBasedAnnualLeaveGrant)
        .where(EntryDateBasedAnnualLeaveGrant.branch_id == branch_id)
        .where(EntryDateBasedAnnualLeaveGrant.deleted_yn == 'N')
    )
    result = await session.execute(stmt)
    policy = result.scalar_one_or_none()

    return policy

async def create(*, session: AsyncSession, branch_id: int, request: EntryDateBasedAnnualLeaveGrant = EntryDateBasedAnnualLeaveGrant()) -> EntryDateBasedAnnualLeaveGrant:

    if request.branch_id is None:
        request.branch_id = branch_id
    session.add(request)
    await session.flush()
    await session.refresh(request)
    return request
    
async def update(*, session: AsyncSession, branch_id: int, request: EntryDateBasedAnnualLeaveGrant, old: EntryDateBasedAnnualLeaveGrant) -> bool:

    # 변경된 필드만 업데이트
    changed_fields = {}
    for column in EntryDateBasedAnnualLeaveGrant.__table__.columns:
        if column.name not in ['id', 'branch_id', 'created_at', 'updated_at', 'deleted_yn']:
            new_value = getattr(request, column.name)
            if new_value is not None and getattr(old, column.name) != new_value:
                changed_fields[column.name] = new_value

    if changed_fields:
        # 변경된 필드가 있을 경우에만 업데이트 수행
        stmt = sa_update(EntryDateBasedAnnualLeaveGrant).where(EntryDateBasedAnnualLeaveGrant.branch_id == branch_id).values(**changed_fields)
        await session.execute(stmt)
        old.updated_at = datetime.now()
        await session.flush()
        await session.refresh(old)
    else:
        pass

    return True