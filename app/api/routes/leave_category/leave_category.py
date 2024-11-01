from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.permissions.auth_utils import available_higher_than
from app.enums.users import Role
from app.service import leave_category_service
from app.schemas.leave_category_schemas import LeaveCategoryDto, LeaveCategoryWithExcludedPartsDto

router = APIRouter()


@router.get("/filtered/list", response_model=list[LeaveCategoryDto], summary="제외파트 필터된 휴무 카테고리 목록 조회")
@available_higher_than(Role.EMPLOYEE)
async def read_filtered_leave_categories(
    *,
    branch_id: int,
    context: Request,
    session: AsyncSession = Depends(get_db)
) -> list[LeaveCategoryDto]:

    if context.state.user.role == Role.EMPLOYEE:
        return await leave_category_service.get_filtered_leave_categories(
            session=session, branch_id=branch_id, user_id=context.state.user.id
        )
    
    return await leave_category_service.get_all_leave_categories(
        session=session, branch_id=branch_id
    )

    
@router.get("/list", response_model=list[LeaveCategoryWithExcludedPartsDto], summary="제외파트 정보 포함 휴무 카테고리 목록 조회")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def read_leave_categories(
    *,
    context: Request,
    branch_id: int,
    session: AsyncSession = Depends(get_db)
) -> list[LeaveCategoryWithExcludedPartsDto]:

    return await leave_category_service.get_all_with_excluded_parts(
        session=session, branch_id=branch_id
    )


@router.post("/create", response_model=LeaveCategoryWithExcludedPartsDto, status_code=201, summary="휴무 카테고리 생성")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def create_leave_category(
    *,
    branch_id: int,
    session: AsyncSession = Depends(get_db),
    request: LeaveCategoryWithExcludedPartsDto,
    context: Request
) -> LeaveCategoryWithExcludedPartsDto:
    
    return await leave_category_service.create_leave_category(
        session=session, branch_id=branch_id, request=request
    )
    

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

    return await leave_category_service.update_leave_category(
        session=session, branch_id=branch_id, leave_category_id=leave_category_id, request=request
    )


@router.delete("/{leave_category_id}/delete", response_model=bool, summary="휴무 카테고리 삭제")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def delete_leave_category(
    *,
    branch_id: int,
    leave_category_id: int,
    session: AsyncSession = Depends(get_db),
    context: Request
) -> bool:

    return await leave_category_service.delete_leave_category(
        session=session, branch_id=branch_id, leave_category_id=leave_category_id
    )
