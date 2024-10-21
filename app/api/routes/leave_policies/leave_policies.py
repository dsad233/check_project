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

class AccountPoliciesWithParts(AccountBasedGrantDto):
    part_ids: List[PartIdWithName] = []

class EntryDatePoliciesWithParts(EntryDateBasedGrantDto):
    part_ids: List[PartIdWithName] = []

class ConditionPoliciesWithParts(ConditionBasedGrantDto):
    part_ids: List[PartIdWithName] = []

class AutoLeavePoliciesAndPartsDto(BaseModel):
    auto_approval_policies: AutoAnnualLeaveApprovalDto
    account_based_policies: AccountPoliciesWithParts
    entry_date_based_policies: EntryDatePoliciesWithParts
    condition_based_policies: ConditionPoliciesWithParts
    manual_based_parts: List[PartIdWithName] = []

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
        account_based_policies=AccountPoliciesWithParts(
            **AccountBasedGrantDto.model_validate(auto_grant_policies or {}).model_dump(),
            part_ids=[PartIdWithName.model_validate(part) for part in (account_parts or [])]
        ),
        entry_date_based_policies=EntryDatePoliciesWithParts(
            **EntryDateBasedGrantDto.model_validate(auto_grant_policies or {}).model_dump(),
            part_ids=[PartIdWithName.model_validate(part) for part in (entry_date_parts or [])]
        ),
        condition_based_policies=ConditionPoliciesWithParts(
            **ConditionBasedGrantDto.model_validate(auto_grant_policies or {}).model_dump(),
            part_ids=[PartIdWithName.model_validate(part) for part in (condition_parts or [])]
        ),
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
    grant_data = {
        **data.account_based_policies.model_dump(exclude={'part_ids'}),
        **data.entry_date_based_policies.model_dump(exclude={'part_ids'}),
        **data.condition_based_policies.model_dump(exclude={'part_ids'})
    }
    
    if auto_annual_leave_grant is None:
        await auto_annual_leave_grant_crud.create(
            session=session,
            branch_id=branch_id,
            auto_annual_leave_grant_create=AutoAnnualLeaveGrant(branch_id=branch_id, **grant_data)
        )
    else:
        await auto_annual_leave_grant_crud.update(
            session=session,
            branch_id=branch_id,
            auto_annual_leave_grant_update=AutoAnnualLeaveGrant(branch_id=branch_id, **grant_data)
        )
    
    # 파트 auto_annual_leave_grant 업데이트
    all_parts = (
        data.account_based_policies.part_ids +
        data.entry_date_based_policies.part_ids +
        data.condition_based_policies.part_ids +
        data.manual_based_parts
    )

    for part in all_parts:
        if part in data.account_based_policies.part_ids:
            grant_type = "회계기준 부여"
        elif part in data.entry_date_based_policies.part_ids:
            grant_type = "입사일 기준 부여"
        elif part in data.condition_based_policies.part_ids:
            grant_type = "조건별 부여"
        else:
            grant_type = "수동부여"
        
        await parts_crud.update_auto_annual_leave_grant(
            session=session,
            branch_id=branch_id,
            part_id=part.id,
            auto_annual_leave_grant=grant_type
        )
        
    return f"{branch_id}번 브랜치의 자동 연차 정책이 업데이트 되었습니다."