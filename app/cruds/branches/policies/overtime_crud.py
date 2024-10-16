from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.branches.overtime_policies_model import (
    OverTimePolicies,
    OverTimePoliciesDto,
)

async def create_overtime_policies(
    *, session: AsyncSession, branch_id: int
) -> OverTimePolicies:
    db_obj = OverTimePolicies(branch_id=branch_id)
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj

async def update_overtime_policies(
    *, session: AsyncSession, branch_id: int, overtime_policies_update: OverTimePoliciesDto
) -> None:
    stmt = select(OverTimePolicies).where(OverTimePolicies.branch_id == branch_id)
    result = await session.execute(stmt)
    db_obj = result.scalar_one_or_none()
    
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Over time policies not found")
    
    update_data = overtime_policies_update.model_dump(exclude_unset=True)

    update_stmt = (
        update(OverTimePolicies)
        .where(OverTimePolicies.branch_id == branch_id)
        .values(**update_data)
    )
    await session.execute(update_stmt)
    await session.commit()
    return


async def get_overtime_policies(
    *, session: AsyncSession, branch_id: int
) -> OverTimePolicies:
    stmt = select(OverTimePolicies).where(OverTimePolicies.branch_id == branch_id)
    result = await session.execute(stmt)
    db_obj = result.scalar_one_or_none()
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Over time policies not found")
    return db_obj