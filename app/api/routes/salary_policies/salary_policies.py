from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.permissions.auth_utils import available_higher_than
from app.cruds.branches.policies.salary_polices_crud import get_all_policies, update_policies
from app.enums.users import Role
from app.models.branches.salary_polices_model import CombinedPoliciesResponse, CombinedPoliciesUpdate
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
    

@router.get("/combined", response_model=CombinedPoliciesResponse)
@available_higher_than(Role.INTEGRATED_ADMIN)
async def read_all_policies(
    context: Request,
    branch_id: int,
    session: AsyncSession = Depends(get_db)
):
    """
    임금 명세서 설정 조회
    """
    policies = await get_all_policies(session, branch_id)
    if not any(policies.values()):
        raise HTTPException(status_code=404, detail="정책을 찾을 수 없습니다")
    return policies

@router.patch("/combined", response_model=CombinedPoliciesResponse)
@available_higher_than(Role.INTEGRATED_ADMIN)
async def update_all_policies(
    context: Request,
    update_data: CombinedPoliciesUpdate,
    branch_id: int,
    session: AsyncSession = Depends(get_db)
):
    """
    임금 명세서 설정 조회
    """
    
    try:
        updated_policies = await update_policies(session, branch_id, update_data)
        return updated_policies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정책 수정 중 오류가 발생했습니다: {str(e)}")
