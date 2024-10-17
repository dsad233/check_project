from typing import Optional

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

async def create_holiday_work_policies_by_value(
    *, session: AsyncSession, branch_id: int, holiday_work_policies_update: HolidayWorkPoliciesDto
) -> None:
    db_obj = HolidayWorkPolicies(branch_id=branch_id, **holiday_work_policies_update.model_dump())
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)

async def update_holiday_work_policies(
    *, session: AsyncSession, branch_id: int, holiday_work_policies_update: HolidayWorkPoliciesDto
) -> None:
    
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
) -> Optional[HolidayWorkPolicies]:
    stmt = select(HolidayWorkPolicies).where(HolidayWorkPolicies.branch_id == branch_id)
    result = await session.execute(stmt)
    db_obj = result.scalar_one_or_none()
    return db_obj