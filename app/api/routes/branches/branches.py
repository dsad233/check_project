import logging
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.common.dto.pagination_dto import PaginationDto
from app.common.dto.search_dto import BaseSearchDto
from app.core.database import get_db
from app.cruds.branches.policies.salary_polices_crud import create_parttimer_policies
from app.schemas.users_schemas import UserLeaveResponse, UsersLeaveResponse
from app.service import user_service
from app.cruds.branches import branches_crud
from app.middleware.tokenVerify import validate_token, get_current_user_id, get_current_user
from app.exceptions.exceptions import ForbiddenError, NotFoundError, BadRequestError
from app.models.users.users_model import Users
from app.enums.users import Role
from app.service import branch_service
from app.models.branches.branches_model import Branches
from app.schemas.branches_schemas import BranchRequest, BranchListResponse, BranchResponse, ManualGrantRequest
from app.core.permissions.auth_utils import available_higher_than


router = APIRouter(dependencies=[Depends(validate_token)])

@router.get("/get", response_model=BranchListResponse, summary="지점 목록 조회")
async def read_branches(
    *, session: AsyncSession = Depends(get_db), search: BaseSearchDto = Depends(BaseSearchDto), user: int = Depends(get_current_user)
) -> BranchListResponse:
    """
    지점 목록을 조회합니다.
    - MSO면 모든 리스트 이외는 해당 지점의 리스트만 반환합니다.
    - **page**: 페이지 번호. 0을 입력하면 페이지네이션 없이 모든 결과를 반환합니다.
    - 기본적으로 페이지네이션이 적용되며, `search` 파라미터를 통해 offset과 record_size를 조정할 수 있습니다.
    """
    if user.role != Role.MSO:
        branch = await branches_crud.find_by_id(session=session, branch_id=user.branch_id)
        if branch is None:
            raise NotFoundError(detail=f"{user.branch_id}번 지점이 없습니다.")
        return BranchListResponse(data=[branch], pagination=PaginationDto(total_record=1))

    return await branch_service.get_branches(session=session, search=search)


@router.post("/create", response_model=bool, status_code=201, summary="지점 생성")
@available_higher_than(Role.MSO)
async def create_branch(
    *, request: Request, session: AsyncSession = Depends(get_db), branch_create: BranchRequest
) -> bool:
    
    return await branch_service.create_branch(session=session, branch_create=branch_create)


@router.get("/{branch_id}/get", response_model=BranchResponse, summary="지점 조회")
async def read_branch(
    *, session: AsyncSession = Depends(get_db), branch_id: int, user: Users = Depends(get_current_user)
) -> BranchResponse:

    branch = await branches_crud.find_by_id(session=session, branch_id=branch_id)
    if branch is None:
        raise NotFoundError(detail=f"{branch_id}번 지점이 없습니다.")
    return branch


@router.patch("/{branch_id}/update", response_model=bool, summary="지점 수정")
@available_higher_than(Role.MSO)
async def update_branch(
    *, request: Request, session: AsyncSession = Depends(get_db), branch_id: int, branch_update: BranchRequest
) -> bool:

    branch = await branches_crud.find_by_id(session=session, branch_id=branch_id)
    if branch is None:
        raise NotFoundError(detail=f"{branch_id}번 지점이 없습니다.")
    
    await branches_crud.update(session=session, branch_id=branch_id, branch_update=Branches(**branch_update.model_dump()))
    return True


@router.delete("/{branch_id}/delete", response_model=bool, summary="지점 삭제")
@available_higher_than(Role.MSO)
async def delete_branch(
    *, request: Request, session: AsyncSession = Depends(get_db), branch_id: int
) -> bool:
    
    branch = await branches_crud.find_by_id(session=session, branch_id=branch_id)
    if branch is None:
        raise NotFoundError(detail=f"{branch_id}번 지점이 없습니다.")
    await branches_crud.delete(session=session, branch_id=branch_id)
    return True


@router.get("/deleted/list", response_model=BranchListResponse, summary="삭제된 지점 목록 조회")
@available_higher_than(Role.MSO)
async def read_deleted_branches(
    *, session: AsyncSession = Depends(get_db), request:Request,  search: BaseSearchDto = Depends(BaseSearchDto)
) -> BranchListResponse:

    count = await branches_crud.count_deleted_all(session=session)
    pagination = PaginationDto(total_record=count)
    branches = await branches_crud.find_deleted_all(
        session=session, search=search
    )
    if branches is None:
        branches = []
    return BranchListResponse(data=branches, pagination=pagination)

    
@router.patch("/{branch_id}/revive", response_model=bool, summary="삭제된 지점 복구")
@available_higher_than(Role.MSO)
async def revive_branch(
    *, request: Request, session: AsyncSession = Depends(get_db), branch_id: int
) -> bool:
    
    branch = await branches_crud.find_by_id(session=session, branch_id=branch_id)
    if branch is None:
        raise NotFoundError(detail=f"{branch_id}번 지점이 없습니다.")
    await branches_crud.revive(session=session, branch_id=branch_id)
    return True


@router.get("/{branch_id}/users/leave", response_model=UsersLeaveResponse, summary="지점 내 유저들의 잔여 연차 수 및 연차 부여 방식 조회")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def read_branch_users_leave(
    *, request: Request, session: AsyncSession = Depends(get_db), branch_id: int, search: BaseSearchDto = Depends(BaseSearchDto)
) -> UsersLeaveResponse:

    return await user_service.get_branch_users_leave(session=session, branch_id=branch_id, search=search)


@router.patch("/{branch_id}/users/leave/plus", response_model=bool, summary="유저 연차 수동 부여")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def manual_grant_annual_leave(
    *, request: Request, session: AsyncSession = Depends(get_db), branch_id: int, manual_grant_request: ManualGrantRequest
) -> bool:
    
    memo = manual_grant_request.memo
    for user_id in manual_grant_request.user_ids:
        await user_service.plus_remaining_annual_leave(session=session, user_id=user_id, count=manual_grant_request.count)
    return True


@router.patch("/{branch_id}/users/leave/minus", response_model=bool, summary="유저 연차 수동 차감")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def manual_minus_annual_leave(
    *, request: Request, session: AsyncSession = Depends(get_db), branch_id: int, manual_minus_request: ManualGrantRequest
) -> bool:
    
    memo = manual_minus_request.memo
    print("=============================================")
    print(manual_minus_request.count)
    for user_id in manual_minus_request.user_ids:
        await user_service.minus_remaining_annual_leave(session=session, user_id=user_id, count=manual_minus_request.count)
    return True

