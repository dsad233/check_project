import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi import APIRouter, Depends, Request
from app.core.permissions.auth_utils import available_higher_than
from app.enums.users import Role
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.branches_schemas import (
    CombinedPoliciesDto,
    ScheduleHolidayUpdateDto,
)
from app.service import branch_service
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/get", response_model=CombinedPoliciesDto, summary="근무정책 조회")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def get_work_policies(
    *,
    context: Request,
    session: AsyncSession = Depends(get_db),
    branch_id: int, 
) -> CombinedPoliciesDto:

    return await branch_service.get_branch_policies(session=session, branch_id=branch_id)


@router.patch("/update", response_model=bool, summary="근무정책 수정")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def update_work_policies(
    *,
    context: Request,
    session: AsyncSession = Depends(get_db),
    branch_id: int,
    request: CombinedPoliciesDto,
) -> bool:
    
    return await branch_service.update_branch_policies(session=session, branch_id=branch_id, request=request)


@router.patch("/holiday", response_model=str, summary="고정 휴점일 수정")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def update_schedule_holiday(
    *,
    context: Request,
    session: AsyncSession = Depends(get_db),
    branch_id: int,
    policies_in: ScheduleHolidayUpdateDto,
) -> str:
    
    return await branch_service.update_schedule_holiday(session=session, branch_id=branch_id, request=policies_in)
