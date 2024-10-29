from datetime import datetime
import logging
from typing import Optional
from fastapi import Depends
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from app.common.dto.search_dto import BaseSearchDto
from app.models.parts.parts_model import Parts
from app.exceptions.exceptions import InvalidEnumValueError, NotFoundError
from app.enums.parts import PartAutoAnnualLeaveGrant


logger = logging.getLogger(__name__)


async def find_by_id_and_branch_id(
    *, session: AsyncSession, branch_id: int, part_id: int
) -> Optional[Parts]:
    stmt = (
        select(Parts)
        .where(Parts.branch_id == branch_id)
        .where(Parts.deleted_yn == 'N')
        .where(Parts.id == part_id)
    )
    result = await session.execute(stmt)
    part = result.scalar_one_or_none()
    
    return part

async def update_auto_annual_leave_grant(
    *, session: AsyncSession, branch_id: int, part_id: int, auto_annual_leave_grant: PartAutoAnnualLeaveGrant
) -> Parts:
        
    # 먼저 해당 Parts가 존재하는지 확인
    part = await find_by_id_and_branch_id(session=session, branch_id=branch_id, part_id=part_id)
    if not part:
        raise NotFoundError(f"{branch_id}번 지점의 {part_id}번 파트가 존재하지 않습니다.")
    
    # Enum 값 검증
    if auto_annual_leave_grant not in PartAutoAnnualLeaveGrant:
        raise InvalidEnumValueError(f"잘못된 자동 부여 정책 ENUM 입니다: {auto_annual_leave_grant}")

    # 현재 값과 비교하여 변경이 필요한 경우에만 업데이트
    if part.auto_annual_leave_grant != auto_annual_leave_grant.value:
        await session.execute(
            update(Parts)
            .where(Parts.id == part_id)
            .values(auto_annual_leave_grant=auto_annual_leave_grant.value)
        )

        await session.commit()
        await session.refresh(part)
    else:
        pass

    return part
    
async def find_all_by_branch_id_and_auto_annual_leave_grant(
    *, session: AsyncSession, branch_id: int, auto_annual_leave_grant: str
) -> Optional[Parts]:
    stmt = (
        select(Parts)
        .where(Parts.branch_id == branch_id)
        .where(Parts.auto_annual_leave_grant == auto_annual_leave_grant)
        .where(Parts.deleted_yn == 'N')
    )
    result = await session.execute(stmt)
    parts = result.scalars().all()
    
    return parts
