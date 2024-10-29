import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.common.dto.pagination_dto import PaginationDto
from app.common.dto.search_dto import BaseSearchDto
from app.core.database import get_db
from app.cruds.branches.policies.salary_polices_crud import create_parttimer_policies
from app.schemas.users_schemas import UserLeaveResponse
from app.service import user_service
from app.cruds.branches import branches_crud
from app.cruds.users import users_crud
from app.cruds.branches.policies import holiday_work_crud, overtime_crud, work_crud, auto_overtime_crud, allowance_crud
from app.cruds.leave_policies import auto_annual_leave_approval_crud, account_based_annual_leave_grant_crud, entry_date_based_annual_leave_grant_crud, condition_based_annual_leave_grant_crud
from app.middleware.tokenVerify import validate_token, get_current_user_id
from app.exceptions.exceptions import ForbiddenError, NotFoundError, BadRequestError
from app.models.branches.branches_model import (
    Branches,
    BranchCreate,
    BranchUpdate, 
    BranchListResponse,
    BranchResponse,
)

router = APIRouter(dependencies=[Depends(validate_token)])

class ManualGrantRequest(BaseModel):
    count: int
    user_ids: list[int]
    memo: Optional[str] = None

async def check_admin_role(*, session: AsyncSession, current_user_id: int):
    user = await users_crud.find_by_id(session=session, user_id=current_user_id)
    if user.role.strip() != "MSO 최고권한":
        raise ForbiddenError(detail="MSO 최고권한만 접근할 수 있습니다.")

@router.get("/get", response_model=BranchListResponse)
async def read_branches(
    *, session: AsyncSession = Depends(get_db), search: BaseSearchDto = Depends(), current_user_id: int = Depends(get_current_user_id)
) -> BranchListResponse:
    """
    지점 목록을 조회합니다.
    - MSO면 모든 리스트 이외는 해당 지점의 리스트만 반환합니다.
    - **page**: 페이지 번호. 0을 입력하면 페이지네이션 없이 모든 결과를 반환합니다.
    - 기본적으로 페이지네이션이 적용되며, `search` 파라미터를 통해 offset과 record_size를 조정할 수 있습니다.
    """
    user = await users_crud.find_by_id(session=session, user_id=current_user_id)
    if user.role.strip() != "MSO 최고권한":
        branch = await branches_crud.find_by_id(session=session, branch_id=user.branch_id)
        if branch is None:
            raise NotFoundError(detail=f"{user.branch_id}번 지점이 없습니다.")
        return BranchListResponse(list=[branch], pagination=PaginationDto(total_record=1))


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
    await account_based_annual_leave_grant_crud.create(session=session, branch_id=branch_id)
    await entry_date_based_annual_leave_grant_crud.create(session=session, branch_id=branch_id)
    await condition_based_annual_leave_grant_crud.create(session=session, branch_id=branch_id)
    await create_parttimer_policies(session, branch_id)
    
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

@router.patch("/{branch_id}/update", response_model=str)
async def update_branch(
    *, session: AsyncSession = Depends(get_db), branch_id: int, branch_update: BranchUpdate, current_user_id: int = Depends(get_current_user_id)
) -> str:
    try:
        await check_admin_role(session=session, current_user_id=current_user_id)

        branch = await branches_crud.find_by_id(session=session, branch_id=branch_id)
        if branch is None:
            raise NotFoundError(detail=f"{branch_id}번 지점이 없습니다.")
        
        updated_branch = await branches_crud.update(session=session, branch_id=branch_id, branch_update=branch_update)
        return f"{updated_branch.id}번 지점이 수정되었습니다."
    except Exception as e:
        print(f"에러 발생: {str(e)}")
        print(f"에러 타입: {type(e).__name__}")
        print(f"에러 발생 위치: {e.__traceback__.tb_frame.f_code.co_filename}, 라인 {e.__traceback__.tb_lineno}")
        raise


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

@router.get("/{branch_id}/users/leave", response_model=list[UserLeaveResponse], summary="지점 내 유저들의 잔여 연차 수 및 연차 부여 방식 조회")
async def read_branch_users_leave(
    *, session: AsyncSession = Depends(get_db), branch_id: int, current_user_id: int = Depends(get_current_user_id)
) -> list[UserLeaveResponse]:
    # await check_admin_role(session=session, current_user_id=current_user_id)
    return await user_service.get_branch_users_leave(session=session, branch_id=branch_id)

@router.patch("/{branch_id}/users/leave/plus", response_model=bool)
async def manual_grant_annual_leave(
    *, session: AsyncSession = Depends(get_db), branch_id: int, manual_grant_request: ManualGrantRequest, current_user_id: int = Depends(get_current_user_id)
) -> bool:
    # await check_admin_role(session=session, current_user_id=current_user_id)
    memo = manual_grant_request.memo
    for user_id in manual_grant_request.user_ids:
        await user_service.plus_remaining_annual_leave(session=session, user_id=user_id, count=manual_grant_request.count)
    return True

@router.patch("/{branch_id}/users/leave/minus", response_model=bool)
async def manual_minus_annual_leave(
    *, session: AsyncSession = Depends(get_db), branch_id: int, manual_minus_request: ManualGrantRequest, current_user_id: int = Depends(get_current_user_id)
) -> bool:
    # await check_admin_role(session=session, current_user_id=current_user_id)
    for user_id in manual_minus_request.user_ids:
        await user_service.minus_remaining_annual_leave(session=session, user_id=user_id, count=manual_minus_request.count)
    return True

