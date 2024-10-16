from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.branches.holiday_work_policies_model import (
    HolidayWorkPolicies,
    HolidayWorkPoliciesDto,
)

async def create_holiday_work_policies(
    *, session: AsyncSession, branch_id: int
) -> HolidayWorkPolicies:
    db_obj = HolidayWorkPolicies(branch_id=branch_id)
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj

async def update_holiday_work_policies(
    *, session: AsyncSession, branch_id: int, holiday_work_policies_update: HolidayWorkPoliciesDto
) -> None:
    stmt = select(HolidayWorkPolicies).where(HolidayWorkPolicies.branch_id == branch_id)
    result = await session.execute(stmt)
    db_obj = result.scalar_one_or_none()

    if db_obj is None:
        raise HTTPException(status_code=404, detail="Holiday work policies not found")
    
    update_data = holiday_work_policies_update.model_dump(exclude_unset=True)

    update_stmt = (
        update(HolidayWorkPolicies)
        .where(HolidayWorkPolicies.branch_id == branch_id)
        .values(**update_data)
    )
    await session.execute(update_stmt)

    await session.commit()
    return

async def get_holiday_work_policies(
    *, session: AsyncSession, branch_id: int
) -> HolidayWorkPolicies:
    stmt = select(HolidayWorkPolicies).where(HolidayWorkPolicies.branch_id == branch_id)
    result = await session.execute(stmt)
    db_obj = result.scalar_one_or_none()
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Holiday work policies not found")
    return db_obj