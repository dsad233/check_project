import logging
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.exceptions import ForbiddenError, NotFoundError, BadRequestError
from app.common.dto.pagination_dto import PaginationDto
from app.common.dto.search_dto import BaseSearchDto
from app.core.database import get_db
from app.cruds.parts import parts_crud
from app.cruds.leave_categories import leave_categories_crud, leave_excluded_parts_crud
from app.cruds.users import users_crud
from app.middleware.tokenVerify import validate_token, get_current_user_id
from app.models.branches.leave_categories_model import (
    LeaveCategory,
    LeaveCategoryDto,
)

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(validate_token)])

class PartIdAndName(BaseModel):
    id: int
    name: Optional[str] = None

    class Config:
        from_attributes = True

class LeaveCategoryWithExcludedPartsDto(BaseModel):
    leave_category: LeaveCategoryDto
    excluded_parts: list[PartIdAndName] = []

async def check_role(*, session: AsyncSession, current_user_id: int, branch_id: int):
    user = await users_crud.find_by_id(session=session, user_id=current_user_id)
    if user.role.strip() == "MSO 최고권한":
        pass
    elif user.role.strip() in ["최고관리자", "파트관리자", "통합관리자"]:
        if user.branch_id != branch_id:
            raise ForbiddenError(detail="다른 지점의 정보에 접근할 수 없습니다.")
    else:
        raise ForbiddenError(detail="권한이 없습니다.")

    
@router.get("/list", response_model=List[LeaveCategoryWithExcludedPartsDto])
async def read_leave_categories(
    *,
    branch_id: int,
    session: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) -> List[LeaveCategoryWithExcludedPartsDto]:
    
    await check_role(session=session, current_user_id=current_user_id, branch_id=branch_id)

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
            PartIdAndName.model_validate(await parts_crud.find_by_id_and_branch_id(
                session=session, branch_id=branch_id, part_id=excluded_part.part_id
            ))
        ) for excluded_part in excluded_parts]
        result.append(LeaveCategoryWithExcludedPartsDto(
            excluded_parts=excluded_parts_data,
            leave_category=LeaveCategoryDto.model_validate(leave_category)
        ))
    return result


@router.post("/create", response_model=str, status_code=201)
async def create_leave_category(
    *,
    branch_id: int,
    session: AsyncSession = Depends(get_db),
    data: LeaveCategoryWithExcludedPartsDto,
    current_user_id: int = Depends(get_current_user_id)
) -> str:
    
    await check_role(session=session, current_user_id=current_user_id, branch_id=branch_id)

    create_in = LeaveCategory(branch_id=branch_id, **data.leave_category.model_dump())
    leave_category_id = await leave_categories_crud.create(
        session=session, branch_id=branch_id, leave_category_create=create_in
    )
    create_excluded_part_ids = [part.id for part in data.excluded_parts]
    if create_excluded_part_ids:
        await leave_excluded_parts_crud.create_all_part_id(
            session=session, leave_category_id=leave_category_id, part_ids=create_excluded_part_ids
        )
    return f"{leave_category_id}번 휴가 카테고리가 생성되었습니다."
    

@router.patch("/{leave_category_id}/update", response_model=str)
async def update_leave_category(
    *,
    branch_id: int,
    leave_category_id: int,
    session: AsyncSession = Depends(get_db),
    data: LeaveCategoryWithExcludedPartsDto,
    current_user_id: int = Depends(get_current_user_id)
) -> str:
    """
    휴무 카테고리를 수정 합니다.

    - leave_category: 수정 할 카테고리 내용을 입력합니다.
    - excluded_parts: 추가 할 제외 부서를 입력합니다. (id, name)
    
    - 오류 발생 시 500 Internal Server Error를 반환합니다.
    """
    
    await check_role(session=session, current_user_id=current_user_id, branch_id=branch_id)

    update_in = LeaveCategory(branch_id=branch_id, **data.leave_category.model_dump(exclude_unset=True))
    await leave_categories_crud.update(
        session=session, branch_id=branch_id, leave_category_id=leave_category_id, leave_category_update=update_in
    )
    # 해당 휴무의 제외 부서 전체 조회
    excluded_parts = await leave_excluded_parts_crud.find_all_by_leave_category_id(
        session=session, leave_category_id=leave_category_id
    )
    
    saved_part_ids = set([excluded_part.part_id for excluded_part in excluded_parts])
    request_part_ids = set([part.id for part in data.excluded_parts])
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
    return f"{leave_category_id}번 휴가 카테고리가 수정되었습니다."



@router.delete("/{leave_category_id}/delete", response_model=str)
async def delete_leave_category(
    *,
    branch_id: int,
    leave_category_id: int,
    session: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) -> str:
    
    await check_role(session=session, current_user_id=current_user_id, branch_id=branch_id)

    await leave_categories_crud.delete(
        session=session, branch_id=branch_id, leave_category_id=leave_category_id
    )
    return f"{leave_category_id}번 휴가 카테고리가 삭제되었습니다."