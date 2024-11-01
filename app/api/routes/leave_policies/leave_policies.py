from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.exceptions import ForbiddenError
from app.core.database import get_db
from app.cruds.users import users_crud
from app.service import branch_service
from app.middleware.tokenVerify import validate_token, get_current_user_id
from app.schemas.branches_schemas import AutoLeavePoliciesAndPartsDto, BranchHistoriesResponse
from app.common.dto.search_dto import BaseSearchDto
from app.enums.branches import BranchHistoryType
from app.core.permissions.auth_utils import available_higher_than
from app.enums.users import Role
from app.models.users.users_model import Users
from app.middleware.tokenVerify import get_current_user


router = APIRouter()

@router.get("/get", response_model=AutoLeavePoliciesAndPartsDto, summary="자동 휴무 정책 및 해당 파트 조회")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def get_auto_leave_policies(
    *,
    branch_id: int,
    session: AsyncSession = Depends(get_db),
    context: Request
) -> AutoLeavePoliciesAndPartsDto:
    try:
    
        return await branch_service.get_auto_leave_policies_and_parts(session=session, branch_id=branch_id)
    except Exception as error:
        print(f"에러 발생!!!!!!!! {error}")

@router.patch("/update", response_model=bool, summary="자동 휴무 정책 및 파트 정책 수정")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def update_auto_leave_policies(
    *,
    branch_id: int,
    request: AutoLeavePoliciesAndPartsDto,
    session: AsyncSession = Depends(get_db),
    user: Users = Depends(get_current_user),
    context: Request
) -> bool:
    
    return await branch_service.update_auto_leave_policies_and_parts(session=session, branch_id=branch_id, request=request, current_user_id=user.id)


@router.get("/histories", response_model=BranchHistoriesResponse, summary="자동 휴무 정책 수정 이력 조회")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def get_branch_histories(
    *,
    branch_id: int,
    request: BaseSearchDto = Depends(BaseSearchDto),
    session: AsyncSession = Depends(get_db),
    context: Request
) -> BranchHistoriesResponse:
    
    return await branch_service.get_branch_histories(session=session, branch_id=branch_id, request=request, history_type=BranchHistoryType.AUTO_ANNUAL_LEAVE_GRANT)
