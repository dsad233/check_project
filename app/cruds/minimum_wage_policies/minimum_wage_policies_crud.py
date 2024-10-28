
from typing import Optional
from datetime import datetime
from fastapi import Depends
from sqlalchemy import func, select, exists, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.common.minimum_wage_policies_model import MinimumWagePolicy
from app.exceptions.exceptions import NotFoundError, BadRequestError

async def find(*, session: AsyncSession) -> Optional[MinimumWagePolicy]:
    print("여기1")
    stmt = (
        select(MinimumWagePolicy).where(MinimumWagePolicy.deleted_yn == "N")
    )
    print("여기2")
    result = await session.execute(stmt)
    print("여기3")
    return result.scalar_one_or_none()

async def update(*, session: AsyncSession, minimum_wage_policy_update: MinimumWagePolicy) -> MinimumWagePolicy:

    minimum_wage_policy = await find(session=session)
    if minimum_wage_policy is None:
        raise NotFoundError(f"최저시급 정책을 찾을 수 없습니다.")
    
    minimum_wage_policy.minimum_wage = minimum_wage_policy_update.minimum_wage
    minimum_wage_policy.person_in_charge = minimum_wage_policy_update.person_in_charge
    minimum_wage_policy.updated_at = datetime.now()
    await session.commit()
    await session.refresh(minimum_wage_policy)
    return minimum_wage_policy