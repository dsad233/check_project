from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.exceptions import ForbiddenError, NotFoundError, BadRequestError
from app.common.dto.pagination_dto import PaginationDto
from app.common.dto.search_dto import BaseSearchDto
from app.core.database import get_db
from app.cruds.parts import parts_crud
from app.cruds.leave_categories import leave_categories_crud, leave_excluded_parts_crud
from app.cruds.users import users_crud
from app.core.permissions.auth_utils import available_higher_than
from app.enums.users import Role
from app.middleware.tokenVerify import validate_token, get_current_user_id
from app.schemas.parts_schemas import PartIdWithName
from app.schemas.branches_schemas import LeaveCategoryDto
from app.models.branches.leave_categories_model import (
    LeaveCategory
)

router = APIRouter()


class LeaveCategoryWithExcludedPartsDto(BaseModel):
    leave_category: LeaveCategoryDto
    excluded_parts: list[PartIdWithName] = []


@router.get("/filtered/list", response_model=list[LeaveCategoryDto], summary="제외파트 필터된 휴무 카테고리 목록 조회")
@available_higher_than(Role.EMPLOYEE)
async def read_filtered_leave_categories(
    *,
    branch_id: int,
    context: Request,
    session: AsyncSession = Depends(get_db)
) -> list[LeaveCategoryDto]:

    if context.user.role == Role.EMPLOYEE:
        leave_categories = await leave_categories_crud.find_all_with_excluded_parts(
            session=session, branch_id=branch_id)
        result = []
        for leave_category in leave_categories:
            if context.user.part_id in [excluded_part.part_id for excluded_part in leave_category.excluded_parts]:
                continue
            result.append(LeaveCategoryDto.model_validate(leave_category))
        return result

    leave_categories = await leave_categories_crud.find_all_by_branch_id(
        session=session, branch_id=branch_id
    )
    return leave_categories

    
@router.get("/list", response_model=list[LeaveCategoryWithExcludedPartsDto], summary="제외파트 정보 포함 휴무 카테고리 목록 조회")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def read_leave_categories(
    *,
    context: Request,
    branch_id: int,
    session: AsyncSession = Depends(get_db)
) -> list[LeaveCategoryWithExcludedPartsDto]:

    leave_categories = await leave_categories_crud.find_all_by_branch_id(
        session=session, branch_id=branch_id
    )
    result = []
    # 제외 부서 id와 이름 추가
    for leave_category in leave_categories:
        # 해당 휴무의 제외 부서 전체 조회
        excluded_parts = await leave_excluded_parts_crud.find_all_by_leave_category_id(
            session=session, leave_category_id=leave_category.id
        )
        # 제외 부서가 가지는 part_id로 이름 추출
        excluded_parts_data = [(
            PartIdWithName.model_validate(await parts_crud.find_by_id_and_branch_id(
                session=session, branch_id=branch_id, part_id=excluded_part.part_id
            ))
        ) for excluded_part in excluded_parts]
        result.append(LeaveCategoryWithExcludedPartsDto(
            excluded_parts=excluded_parts_data,
            leave_category=LeaveCategoryDto.model_validate(leave_category)
        ))
    return result


@router.post("/create", response_model=LeaveCategoryWithExcludedPartsDto, status_code=201, summary="휴무 카테고리 생성")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def create_leave_category(
    *,
    branch_id: int,
    session: AsyncSession = Depends(get_db),
    request: LeaveCategoryWithExcludedPartsDto,
    context: Request
) -> LeaveCategoryWithExcludedPartsDto:
    
    leave_category = await leave_categories_crud.create(
        session=session, branch_id=branch_id, request=LeaveCategory(branch_id=branch_id, **request.leave_category.model_dump())
    )
    leave_category_id = leave_category.id
    create_excluded_part_ids = [part.id for part in request.excluded_parts]
    if create_excluded_part_ids:
        await leave_excluded_parts_crud.create_all_part_id(
            session=session, leave_category_id=leave_category_id, part_ids=create_excluded_part_ids
        )
    return request
    

@router.patch("/{leave_category_id}/update", response_model=bool, summary="휴무 카테고리 수정")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def update_leave_category(
    *,
    branch_id: int,
    leave_category_id: int,
    session: AsyncSession = Depends(get_db),
    request: LeaveCategoryWithExcludedPartsDto,
    context: Request
) -> bool:
    """
    휴무 카테고리를 수정 합니다.

    - leave_category: 수정 할 카테고리 내용을 입력합니다.
    - excluded_parts: 추가 할 제외 부서를 입력합니다. (id, name)
    
    - 오류 발생 시 500 Internal Server Error를 반환합니다.
    """

    await leave_categories_crud.update(
        session=session, branch_id=branch_id, leave_category_id=leave_category_id, request=LeaveCategory(branch_id=branch_id, **request.leave_category.model_dump(exclude_unset=True))
    )
    # 해당 휴무의 제외 부서 전체 조회
    excluded_parts = await leave_excluded_parts_crud.find_all_by_leave_category_id(
        session=session, leave_category_id=leave_category_id
    )
    
    saved_part_ids = set([excluded_part.part_id for excluded_part in excluded_parts])
    request_part_ids = set([part.id for part in request.excluded_parts])
    #삭제하거나 추가할 부서 id 추출
    part_ids_to_delete = saved_part_ids - request_part_ids
    part_ids_to_create = request_part_ids - saved_part_ids

    if part_ids_to_delete:
        await leave_excluded_parts_crud.delete_all_part_id(
            session=session, leave_category_id=leave_category_id, part_ids=part_ids_to_delete
        )
    if part_ids_to_create:
        await leave_excluded_parts_crud.create_all_part_id(
            session=session, leave_category_id=leave_category_id, part_ids=part_ids_to_create
        )
    return True



@router.delete("/{leave_category_id}/delete", response_model=bool, summary="휴무 카테고리 삭제")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def delete_leave_category(
    *,
    branch_id: int,
    leave_category_id: int,
    session: AsyncSession = Depends(get_db),
    context: Request
) -> bool:

    await leave_categories_crud.delete(
        session=session, branch_id=branch_id, leave_category_id=leave_category_id
    )
    return True