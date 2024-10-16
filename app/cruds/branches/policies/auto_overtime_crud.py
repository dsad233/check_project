from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.branches.auto_overtime_policies_model import (
    AutoOvertimePolicies,
    AutoOvertimePoliciesDto,
)

async def create_auto_overtime_policies(
    *, session: AsyncSession, branch_id: int
) -> AutoOvertimePolicies:
    db_obj = AutoOvertimePolicies(branch_id=branch_id)
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj

async def update_auto_overtime_policies(
    *, session: AsyncSession, branch_id: int, auto_overtime_policies_update: AutoOvertimePoliciesDto
) -> None:
    stmt = select(AutoOvertimePolicies).where(AutoOvertimePolicies.branch_id == branch_id)
    result = await session.execute(stmt)
    db_obj = result.scalar_one_or_none()

    if db_obj is None:
        raise HTTPException(status_code=404, detail="Auto overtime policies not found")
    
    update_data = auto_overtime_policies_update.model_dump(exclude_unset=True)

    update_stmt = (
        update(AutoOvertimePolicies)
        .where(AutoOvertimePolicies.branch_id == branch_id)
        .values(**update_data)
    )

    await session.execute(update_stmt)

    await session.commit()
    return

async def get_auto_overtime_policies(
    *, session: AsyncSession, branch_id: int
) -> AutoOvertimePolicies:
    stmt = select(AutoOvertimePolicies).where(AutoOvertimePolicies.branch_id == branch_id)
    result = await session.execute(stmt)
    db_obj = result.scalar_one_or_none()
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Auto overtime policies not found")
    return db_obj