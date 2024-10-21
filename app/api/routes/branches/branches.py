import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dto.pagination_dto import PaginationDto
from app.common.dto.search_dto import BaseSearchDto
from app.core.database import get_db
from app.cruds.branches import branches_crud
from app.cruds.users import users_crud
from app.cruds.branches.policies import holiday_work_crud, overtime_crud, work_crud, auto_overtime_crud, allowance_crud
from app.cruds.leave_policies import auto_annual_leave_approval_crud, auto_annual_leave_grant_crud
from app.middleware.tokenVerify import validate_token, get_current_user_id
from app.exceptions.exceptions import ForbiddenError, NotFoundError, BadRequestError
from app.models.branches.branches_model import (
    Branches,
    BranchCreate,
    BranchListResponse,
    BranchResponse,
)

router = APIRouter(dependencies=[Depends(validate_token)])

async def check_admin_role(*, session: AsyncSession, current_user_id: int):
    user = await users_crud.find_by_id(session=session, user_id=current_user_id)
    if user.role.strip() != "MSO 최고권한":
        raise ForbiddenError(detail="MSO 최고권한만 접근할 수 있습니다.")

@router.get("/list", response_model=BranchListResponse)
async def read_branches(
    *, session: AsyncSession = Depends(get_db), search: BaseSearchDto = Depends(), current_user_id: int = Depends(get_current_user_id)
) -> BranchListResponse:
    """
    지점 목록을 조회합니다.

    - **page**: 페이지 번호. 0을 입력하면 페이지네이션 없이 모든 결과를 반환합니다.
    - 기본적으로 페이지네이션이 적용되며, `search` 파라미터를 통해 offset과 record_size를 조정할 수 있습니다.
    """
    await check_admin_role(session=session, current_user_id=current_user_id)

    count = await branches_crud.count_all(session=session)
    if search.page == 0:
        branches = await branches_crud.find_all(session=session)
        pagination = PaginationDto(total_record=count, record_size=count)
    else:
        branches = await branches_crud.find_all_by_limit(
        session=session, offset=search.offset, limit=search.record_size
        )
        pagination = PaginationDto(total_record=count)
    if branches is None:
        branches = []
    return BranchListResponse(list=branches, pagination=pagination)


@router.post("/create", response_model=str, status_code=201)
async def create_branch(
    *, session: AsyncSession = Depends(get_db), branch_in: BranchCreate, current_user_id: int = Depends(get_current_user_id)
) -> str:
    
    await check_admin_role(session=session, current_user_id=current_user_id)

    create_in = Branches(**branch_in.model_dump())
    branch = await branches_crud.create(session=session, branch_create=create_in)
    branch_id = branch.id
    # 정책 생성
    await holiday_work_crud.create(session=session, branch_id=branch_id)
    await overtime_crud.create(session=session, branch_id=branch_id)
    await work_crud.create(session=session, branch_id=branch_id)
    await auto_overtime_crud.create(session=session, branch_id=branch_id)
    await allowance_crud.create(session=session, branch_id=branch_id)
    await auto_annual_leave_approval_crud.create(session=session, branch_id=branch_id)
    await auto_annual_leave_grant_crud.create(session=session, branch_id=branch_id)
    return f"{branch_id}번 지점이 생성되었습니다."


@router.get("/{branch_id}/get", response_model=BranchResponse)
async def read_branch(
    *, session: AsyncSession = Depends(get_db), branch_id: int, current_user_id: int = Depends(get_current_user_id)
) -> BranchResponse:
    
    await check_admin_role(session=session, current_user_id=current_user_id)

    branch = await branches_crud.find_by_id(session=session, branch_id=branch_id)
    if branch is None:
        raise NotFoundError(detail=f"{branch_id}번 지점이 없습니다.")
    return branch

@router.delete("/{branch_id}/delete", response_model=str)
async def delete_branch(
    *, session: AsyncSession = Depends(get_db), branch_id: int, current_user_id: int = Depends(get_current_user_id)
) -> None:
    
    await check_admin_role(session=session, current_user_id=current_user_id)
    
    branch = await branches_crud.find_by_id(session=session, branch_id=branch_id)
    if branch is None:
        raise NotFoundError(detail=f"{branch_id}번 지점이 없습니다.")
    await branches_crud.delete(session=session, branch_id=branch_id)
    return f"{branch_id}번 지점이 삭제되었습니다."


@router.get("/deleted/list", response_model=BranchListResponse)
async def read_deleted_branches(
    *, session: AsyncSession = Depends(get_db), search: BaseSearchDto = Depends(), current_user_id: int = Depends(get_current_user_id)
) -> BranchListResponse:
    
    await check_admin_role(session=session, current_user_id=current_user_id)
    
    count = await branches_crud.count_deleted_all(session=session)
    pagination = PaginationDto(total_record=count)
    branches = await branches_crud.find_deleted_all(
    session=session, offset=search.offset, limit=search.record_size
    )
    if branches is None:
        branches = []
    return BranchListResponse(list=branches, pagination=pagination)
    
@router.patch("/{branch_id}/revive", response_model=str)
async def revive_branch(
    *, session: AsyncSession = Depends(get_db), branch_id: int, current_user_id: int = Depends(get_current_user_id)
) -> str:
    
    await check_admin_role(session=session, current_user_id=current_user_id)
    
    branch = await branches_crud.find_by_id(session=session, branch_id=branch_id)
    if branch is None:
        raise NotFoundError(detail=f"{branch_id}번 지점이 없습니다.")
    await branches_crud.revive(session=session, branch_id=branch_id)
    return f"{branch_id}번 지점이 복구되었습니다."