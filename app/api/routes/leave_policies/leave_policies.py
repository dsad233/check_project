import logging
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.exceptions import ForbiddenError
from app.core.database import get_db
from app.cruds.users import users_crud
from app.service import branch_service
from app.middleware.tokenVerify import validate_token, get_current_user_id
from app.schemas.branches_schemas import AutoLeavePoliciesAndPartsDto

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(validate_token)])


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
    
    return await branch_service.get_auto_leave_policies_and_parts(session=session, branch_id=branch_id)

@router.patch("/update", response_model=bool)
async def update_auto_leave_policies(
    branch_id: int,
    data: AutoLeavePoliciesAndPartsDto,
    session: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) -> bool:
    
    await check_role(session=session, current_user_id=current_user_id, branch_id=branch_id)
    
    return await branch_service.update_auto_leave_policies_and_parts(session=session, branch_id=branch_id, data=data)