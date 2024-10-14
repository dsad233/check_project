from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.cruds.leave_categories import leave_categories_crud
from typing import Any
from app.common.dto.pagination_dto import PaginationDto
from app.common.dto.search_dto import BaseSearchDto

from app.models.branches.leave_categories_model import LeaveCreate, LeaveListResponse, LeaveResponse
from app.core.database import get_db
from app.middleware.tokenVerify import validate_token

import logging

logger = logging.getLogger(__name__)

# router = APIRouter(dependencies=[Depends(validate_token)])
router = APIRouter()

@router.get("/", response_model=LeaveListResponse)
async def read_leave_categories(*, branch_id: int, session: AsyncSession = Depends(get_db), search: BaseSearchDto = Depends()) -> LeaveListResponse:
    count = await leave_categories_crud.count_leave_category_all(session=session, branch_id=branch_id)
    pagination = PaginationDto(total_record=count)
    leave_categories = await leave_categories_crud.find_leave_category_all(session=session, branch_id=branch_id, search=search)
    return LeaveListResponse(list=leave_categories, pagination=pagination)

@router.post("/", response_model=LeaveResponse, status_code=201)
async def create_leave_category(*, branch_id: int, session: AsyncSession = Depends(get_db), leave_create: LeaveCreate) -> LeaveResponse:
    return await leave_categories_crud.create_leave_category(session=session, branch_id=branch_id, leave_create=leave_create)

@router.get("/{leave_id}", response_model=LeaveResponse)
async def read_leave_category(*, branch_id: int, leave_id: int, session: AsyncSession = Depends(get_db)) -> LeaveResponse:
    return await leave_categories_crud.find_leave_category_by_id(session=session, branch_id=branch_id, leave_id=leave_id)
