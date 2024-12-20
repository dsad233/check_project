from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.common.dto.pagination_dto import PaginationDto
from app.common.dto.search_dto import BaseSearchDto
from app.core.database import get_db
from app.cruds.branches.policies.salary_polices_crud import create_parttimer_policies
from app.schemas.users_schemas import UserLeaveResponse, UsersLeaveResponse
from app.cruds.branches.policies.salary_polices_crud import create_parttimer_policies
from app.schemas.users_schemas import UserLeaveResponse
from app.service import user_service
from app.enums.users import Role
from app.service import branch_service
from app.schemas.branches_schemas import (
    BranchRequest, BranchListResponse, 
    BranchResponse, ManualGrantRequest, 
    PersonnelRecordCategoryRequest, PersonnelRecordCategoryResponse, 
    PersonnelRecordCategoriesResponse,
)
from app.schemas.users_schemas import (
    PersonnelRecordUsersRequest, PersonnelRecordUsersResponse,
    UsersNameResponse
)
from app.core.permissions.auth_utils import available_higher_than


router = APIRouter()

@router.get("/get", response_model=BranchListResponse, summary="지점 목록 조회")
async def read_branches(
    *, context: Request, session: AsyncSession = Depends(get_db), request: BaseSearchDto = Depends(BaseSearchDto)
) -> BranchListResponse:
    """
    지점 목록을 조회합니다.
    - MSO면 모든 리스트 이외는 해당 지점의 리스트만 반환합니다.
    - **page**: 페이지 번호. 0을 입력하면 페이지네이션 없이 모든 결과를 반환합니다.
    - 기본적으로 페이지네이션이 적용되며, `search` 파라미터를 통해 offset과 record_size를 조정할 수 있습니다.
    """
    if context.state.user.role != Role.MSO:
        branch = await branch_service.get_branch_by_id(session=session, branch_id=context.state.user.branch_id)
        return BranchListResponse(data=[branch], pagination=PaginationDto(total_record=1))

    return await branch_service.get_branches(session=session, request=request)


@router.post("/create", response_model=bool, status_code=201, summary="지점 생성")
@available_higher_than(Role.MSO)
async def create_branch(
    *, context: Request, session: AsyncSession = Depends(get_db), request: BranchRequest
) -> BranchResponse:
    
    return await branch_service.create_branch(session=session, request=request)


@router.get("/{branch_id}/get", response_model=BranchResponse, summary="지점 조회")
async def read_branch(
    *, context: Request, session: AsyncSession = Depends(get_db), branch_id: int
) -> BranchResponse:

    return await branch_service.get_branch_by_id(session=session, branch_id=branch_id)


@router.patch("/{branch_id}/update", response_model=bool, summary="지점 수정")
@available_higher_than(Role.MSO)
async def update_branch(
    *, context: Request, session: AsyncSession = Depends(get_db), branch_id: int, request: BranchRequest
) -> bool:

    return await branch_service.update_branch(session=session, branch_id=branch_id, request=request)


@router.delete("/{branch_id}/delete", response_model=bool, summary="지점 삭제")
@available_higher_than(Role.MSO)
async def delete_branch(
    *, context: Request, session: AsyncSession = Depends(get_db), branch_id: int
) -> bool:
    
    return await branch_service.delete_branch(session=session, branch_id=branch_id)


@router.get("/deleted/list", response_model=BranchListResponse, summary="삭제된 지점 목록 조회")
@available_higher_than(Role.MSO)
async def read_deleted_branches(
    *, context: Request,  session: AsyncSession = Depends(get_db), request: BaseSearchDto = Depends(BaseSearchDto)
) -> BranchListResponse:

    return await branch_service.get_deleted_branches(session=session, request=request)

    
@router.patch("/{branch_id}/revive", response_model=bool, summary="삭제된 지점 복구")
@available_higher_than(Role.MSO)
async def revive_branch(
    *, context: Request, session: AsyncSession = Depends(get_db), branch_id: int
) -> bool:
    
    return await branch_service.revive_branch(session=session, branch_id=branch_id)


@router.get("/{branch_id}/users/leave", response_model=UsersLeaveResponse, summary="지점 내 유저들의 잔여 연차 수 및 연차 부여 방식 조회")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def read_branch_users_leave(
    *, context: Request, session: AsyncSession = Depends(get_db), branch_id: int, request: BaseSearchDto = Depends(BaseSearchDto)
) -> UsersLeaveResponse:

    return await user_service.get_branch_users_leave(session=session, branch_id=branch_id, request=request)


@router.patch("/{branch_id}/users/leave/plus", response_model=bool, summary="유저 연차 수동 부여")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def manual_grant_annual_leave(
    *, context: Request, session: AsyncSession = Depends(get_db), branch_id: int, request: ManualGrantRequest
) -> bool:
    
    return await user_service.plus_total_leave_days(session=session, request=request)


@router.patch("/{branch_id}/users/leave/minus", response_model=bool, summary="유저 연차 수동 차감")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def manual_minus_annual_leave(
    *, context: Request, session: AsyncSession = Depends(get_db), branch_id: int, request: ManualGrantRequest
) -> bool:
    
    return await user_service.minus_total_leave_days(session=session, request=request)


@router.post("/{branch_id}/personnel-record-categories/create", response_model=PersonnelRecordCategoryResponse, summary="지점 인사기록 카테고리 생성")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def create_personnel_record_category(
    *, context: Request, session: AsyncSession = Depends(get_db), branch_id: int, request: PersonnelRecordCategoryRequest
) -> PersonnelRecordCategoryResponse:

    return await branch_service.create_personnel_record_category(session=session, branch_id=branch_id, request=request)


@router.get("/{branch_id}/personnel-record-categories/list", response_model=PersonnelRecordCategoriesResponse, summary="지점 인사기록 카테고리 목록 조회")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def read_personnel_record_categories(
    *, context: Request, session: AsyncSession = Depends(get_db), branch_id: int, request: BaseSearchDto = Depends(BaseSearchDto)
) -> PersonnelRecordCategoriesResponse:

    return await branch_service.get_personnel_record_categories(session=session, branch_id=branch_id, request=request)


@router.patch("/{branch_id}/personnel-record-categories/{personnel_record_category_id}/update", response_model=bool, summary="지점 인사기록 카테고리 수정")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def update_personnel_record_category(
    *, context: Request, session: AsyncSession = Depends(get_db), branch_id: int, personnel_record_category_id: int, request: PersonnelRecordCategoryRequest
) -> bool:

    return await branch_service.update_personnel_record_category(session=session, branch_id=branch_id, personnel_record_category_id=personnel_record_category_id, request=request)


@router.delete("/{branch_id}/personnel-record-categories/{personnel_record_category_id}/delete", response_model=bool, summary="지점 인사기록 카테고리 삭제")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def delete_personnel_record_category(
    *, context: Request, session: AsyncSession = Depends(get_db), branch_id: int, personnel_record_category_id: int
) -> bool:

    return await branch_service.delete_personnel_record_category(session=session, branch_id=branch_id, personnel_record_category_id=personnel_record_category_id)


@router.get("/personnel-record-users/list", response_model=PersonnelRecordUsersResponse, summary="지점 인사관리 페이지 유저 목록 조회")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def read_personnel_record_users(
    *, context: Request, session: AsyncSession = Depends(get_db), request: PersonnelRecordUsersRequest = Depends(PersonnelRecordUsersRequest)
) -> PersonnelRecordUsersResponse:
    
    current_user = context.state.user
    
    if request.branch_id is None:
        if current_user.role != Role.MSO:
            request.branch_id = current_user.branch_id

    return await user_service.get_personnel_record_users(session=session, request=request)


@router.get("/{branch_id}/users/name/list", response_model=UsersNameResponse, summary="지점 내 유저 이름 목록 조회")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def read_branch_users_name(
    *, context: Request, session: AsyncSession = Depends(get_db), branch_id: int, request: BaseSearchDto = Depends(BaseSearchDto)
) -> UsersNameResponse:

    return await user_service.get_branch_users_name(session=session, request=request, branch_id=branch_id)