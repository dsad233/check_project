from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.branches.work_policies_model import (
    WorkPolicies,
    WorkPoliciesDto,
)

async def create_work_policies(
    *, session: AsyncSession, branch_id: int
) -> WorkPolicies:
    db_obj = WorkPolicies(branch_id=branch_id)
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj

async def update_work_policies(
    *, session: AsyncSession, branch_id: int, work_policies_update: WorkPoliciesDto
) -> None:
    stmt = select(WorkPolicies).where(WorkPolicies.branch_id == branch_id)
    result = await session.execute(stmt)
    db_obj = result.scalar_one_or_none()
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Work policies not found")
    
    update_data = work_policies_update.model_dump(exclude_unset=True)

    update_stmt = (
        update(WorkPolicies)
        .where(WorkPolicies.branch_id == branch_id)
        .values(**update_data)
    )
    await session.execute(update_stmt)
    await session.commit()
    return


async def get_work_policies(
    *, session: AsyncSession, branch_id: int
) -> WorkPolicies:
    stmt = select(WorkPolicies).where(WorkPolicies.branch_id == branch_id)
    result = await session.execute(stmt)
    db_obj = result.scalar_one_or_none()
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Work policies not found")
    return db_obj