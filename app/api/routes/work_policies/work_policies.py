from fastapi import APIRouter, Depends, Request
from app.core.permissions.auth_utils import available_higher_than
from app.enums.users import Role
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.branches_schemas import CombinedPoliciesDto
from app.service import branch_service


router = APIRouter()


@router.get("/get", response_model=CombinedPoliciesDto, summary="근무 정책 조회")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def get_work_policies(*,
    session: AsyncSession = Depends(get_db),
    context: Request,
    branch_id: int
) -> CombinedPoliciesDto:
        
    return await branch_service.get_branch_policies(session=session, branch_id=branch_id)
    
    
@router.patch("/update", response_model=bool, summary="근무 정책 수정")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def update_work_policies(*,
    session: AsyncSession = Depends(get_db),
    branch_id: int,
    request: CombinedPoliciesDto,
    context: Request
) -> bool:

    return await branch_service.update_branch_policies(session=session, branch_id=branch_id, request=request)
