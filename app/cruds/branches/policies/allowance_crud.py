from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.branches.allowance_policies_model import ( AllowancePolicies, AllowancePoliciesDto, DefaultAllowancePoliciesDto, HolidayAllowancePoliciesDto
)

async def create_allowance_policies(
    *, session: AsyncSession, branch_id: int
) -> AllowancePolicies:
    db_obj = AllowancePolicies(branch_id=branch_id)

    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj

async def create_allowance_policies_by_value(
    *, session: AsyncSession, branch_id: int, default_allowance_update: DefaultAllowancePoliciesDto, holiday_allowance_update: HolidayAllowancePoliciesDto
) -> None:
    db_obj = AllowancePolicies(branch_id=branch_id, **default_allowance_update.model_dump(), **holiday_allowance_update.model_dump())
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    
async def update_allowance_policies(
    *, session: AsyncSession, branch_id: int, default_allowance_update: DefaultAllowancePoliciesDto, holiday_allowance_update: HolidayAllowancePoliciesDto
) -> None:
    update_data = {
        **default_allowance_update.model_dump(exclude_unset=True),
        **holiday_allowance_update.model_dump(exclude_unset=True)
    }

    update_stmt = (
        update(AllowancePolicies)
        .where(AllowancePolicies.branch_id == branch_id)
        .values(**update_data)
    )
    await session.execute(update_stmt)

    await session.commit()
    return
   

async def get_allowance_policies(
    *, session: AsyncSession, branch_id: int
) -> Optional[AllowancePolicies]:
    stmt = select(AllowancePolicies).where(AllowancePolicies.branch_id == branch_id)
    result = await session.execute(stmt)
    db_obj = result.scalar_one_or_none()
    return db_obj