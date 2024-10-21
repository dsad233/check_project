import logging
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.exceptions import ForbiddenError
from app.core.database import get_db
from app.cruds.parts import parts_crud
from app.cruds.users import users_crud
from app.cruds.leave_policies import auto_annual_leave_approval_crud, auto_annual_leave_grant_crud
from app.middleware.tokenVerify import validate_token, get_current_user_id
from app.models.branches.auto_annual_leave_approval_model import AutoAnnualLeaveApprovalDto, AutoAnnualLeaveApproval
from app.models.branches.auto_annual_leave_grant_model import (
    AccountBasedGrantDto,
    EntryDateBasedGrantDto,
    ConditionBasedGrantDto,
    AutoAnnualLeaveGrantCombined,
    AutoAnnualLeaveGrant
)

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(validate_token)])

class PartIdWithName(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class AutoLeavePoliciesAndPartsDto(BaseModel):
    auto_approval_policies: AutoAnnualLeaveApprovalDto
    account_based_policies: AccountBasedGrantDto
    account_based_parts: List[PartIdWithName]
    entry_date_based_policies: EntryDateBasedGrantDto
    entry_date_based_parts: List[PartIdWithName]
    condition_based_policies: ConditionBasedGrantDto
    condition_based_parts: List[PartIdWithName]
    manual_based_parts: List[PartIdWithName]

async def check_role(*, session: AsyncSession, current_user_id: int, branch_id: int):
    user = await users_crud.find_by_id(session=session, user_id=current_user_id)
    if user.role.strip() == "MSO 최고권한":
        pass
    elif user.role.strip() in ["최고관리자", "파트관리자", "통합관리자"]:
        if user.branch_id != branch_id:
            raise ForbiddenError(detail="다른 지점의 정보에 접근할 수 없습니다.")
    else:
        raise ForbiddenError(detail="권한이 없습니다.")

@router.get("/get", response_model=AutoLeavePoliciesAndPartsDto)
async def get_auto_leave_policies(
    branch_id: int,
    session: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) -> AutoLeavePoliciesAndPartsDto:
    
    await check_role(session=session, current_user_id=current_user_id, branch_id=branch_id)
    
    # 정책 전체 조회
    auto_approval_policies: AutoAnnualLeaveApproval = await auto_annual_leave_approval_crud.find_by_branch_id(session=session, branch_id=branch_id)
    auto_grant_policies: AutoAnnualLeaveGrant = await auto_annual_leave_grant_crud.find_by_branch_id(session=session, branch_id=branch_id)
    auto_annual_leave_grant = ["회계기준 부여", "입사일 기준 부여", "조건별 부여" , "수동부여"]
    # 파트 조회
    account_parts = await parts_crud.find_all_by_branch_id_and_auto_annual_leave_grant(session=session, branch_id=branch_id, auto_annual_leave_grant="회계기준 부여")
    entry_date_parts = await parts_crud.find_all_by_branch_id_and_auto_annual_leave_grant(session=session, branch_id=branch_id, auto_annual_leave_grant="입사일 기준 부여")
    condition_parts = await parts_crud.find_all_by_branch_id_and_auto_annual_leave_grant(session=session, branch_id=branch_id, auto_annual_leave_grant="조건별 부여")
    manual_parts = await parts_crud.find_all_by_branch_id_and_auto_annual_leave_grant(session=session, branch_id=branch_id, auto_annual_leave_grant="수동부여")
    

    return AutoLeavePoliciesAndPartsDto(
        auto_approval_policies=AutoAnnualLeaveApprovalDto.model_validate(auto_approval_policies or {}),
        account_based_policies=AccountBasedGrantDto.model_validate(auto_grant_policies or {}),
        account_based_parts=[PartIdWithName.model_validate(part) for part in (account_parts or [])],
        entry_date_based_policies=EntryDateBasedGrantDto.model_validate(auto_grant_policies or {}),
        entry_date_based_parts=[PartIdWithName.model_validate(part) for part in (entry_date_parts or [])],
        condition_based_policies=ConditionBasedGrantDto.model_validate(auto_grant_policies or {}),
        condition_based_parts=[PartIdWithName.model_validate(part) for part in (condition_parts or [])],
        manual_based_parts=[PartIdWithName.model_validate(part) for part in (manual_parts or [])]
    )

@router.patch("/update", response_model=str)
async def update_auto_leave_policies(
    branch_id: int,
    data: AutoLeavePoliciesAndPartsDto,
    session: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) -> str:
    
    await check_role(session=session, current_user_id=current_user_id, branch_id=branch_id)
    
    auto_annual_leave_approval = await auto_annual_leave_approval_crud.find_by_branch_id(session=session, branch_id=branch_id)
    auto_annual_leave_grant = await auto_annual_leave_grant_crud.find_by_branch_id(session=session, branch_id=branch_id)

    # 자동 승인 정책 업데이트
    if auto_annual_leave_approval is None:
        await auto_annual_leave_approval_crud.create(session=session, branch_id=branch_id, auto_annual_leave_approval_create=AutoAnnualLeaveApproval(branch_id=branch_id, **data.auto_approval_policies.model_dump()))
    else:
        await auto_annual_leave_approval_crud.update(session=session, branch_id=branch_id, auto_annual_leave_approval_update=AutoAnnualLeaveApproval(branch_id=branch_id, **data.auto_approval_policies.model_dump(exclude_unset=True)))

    # 자동 부여 정책 업데이트
    if auto_annual_leave_grant is None:
        await auto_annual_leave_grant_crud.create(session=session, branch_id=branch_id, auto_annual_leave_grant_create=AutoAnnualLeaveGrant(
            branch_id=branch_id,
            **data.account_based_policies.model_dump(),
            **data.entry_date_based_policies.model_dump(),
            **data.condition_based_policies.model_dump()
            )
        )
    else:
        await auto_annual_leave_grant_crud.update(session=session, branch_id=branch_id, auto_annual_leave_grant_update=AutoAnnualLeaveGrant(
            branch_id=branch_id,
            **data.account_based_policies.model_dump(exclude_unset=True),
            **data.entry_date_based_policies.model_dump(exclude_unset=True),
            **data.condition_based_policies.model_dump(exclude_unset=True)
            )
        )
    
    # 파트 auto_annual_leave_grant 업데이트
    for part in data.account_based_parts:
        await parts_crud.update_auto_annual_leave_grant(session=session, branch_id=branch_id, part_id=part.id, auto_annual_leave_grant="회계기준 부여")
    for part in data.entry_date_based_parts:
        await parts_crud.update_auto_annual_leave_grant(session=session, branch_id=branch_id, part_id=part.id, auto_annual_leave_grant="입사일 기준 부여")
    for part in data.condition_based_parts:
        await parts_crud.update_auto_annual_leave_grant(session=session, branch_id=branch_id, part_id=part.id, auto_annual_leave_grant="조건별 부여")
    for part in data.manual_based_parts:
        await parts_crud.update_auto_annual_leave_grant(session=session, branch_id=branch_id, part_id=part.id, auto_annual_leave_grant="수동부여")

    return f"{branch_id}번 브랜치의 자동 연차 정책이 업데이트 되었습니다."