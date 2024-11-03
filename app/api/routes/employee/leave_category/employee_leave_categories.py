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
# @available_higher_than(Role.EMPLOYEE)
async def read_employee_filtered_leave_categories(
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