from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.cruds.branches import crud
from typing import Any
from app.common.dto.pagination_dto import PaginationDto
from app.common.dto.search_dto import BaseSearchDto

from app.api.routes.branches.schema.branch_schema import BranchCreate, BranchDelete, BranchListResponse, BranchResponse
from app.core.database import get_db
from app.middleware.tokenVerify import validate_token

import logging

logger = logging.getLogger(__name__)

# router = APIRouter(dependencies=[Depends(validate_token)])
router = APIRouter()

@router.get("/", response_model=BranchListResponse)
async def read_branches(*, session: AsyncSession = Depends(get_db), page: int = 1) -> BranchListResponse:
    count = await crud.count_branch_all(session=session)
    search = BaseSearchDto(page=page)
    pagination = PaginationDto(total_record=count)
    branches = await crud.find_branch_all(session=session, offset=search.offset, limit=search.limit)
    
    return BranchListResponse(list=branches, pagination=pagination)

@router.post("/", response_model=BranchResponse, status_code=201)
async def create_branch(*, session: AsyncSession = Depends(get_db), branch_in: BranchCreate) -> BranchResponse:
    return await crud.create_branch(session=session, branch_create=branch_in)

@router.get("/{branch_id}", response_model=BranchResponse)
async def read_branch(*, session: AsyncSession = Depends(get_db), branch_id: int) -> BranchResponse:
    branch = await crud.find_branch_by_id(session=session, branch_id=branch_id)
    if branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch

@router.delete("/{branch_id}", status_code=204)
async def delete_branch(*, session: AsyncSession = Depends(get_db), branch_id: int) -> None:
    branch = await crud.find_branch_by_id(session=session, branch_id=branch_id)
    if branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")
    await crud.delete_branch(session=session, branch=branch)

@router.get("/deleted", response_model=BranchListResponse)
async def read_deleted_branches(*, session: AsyncSession = Depends(get_db), page: int = 1) -> BranchListResponse:
    count = await crud.count_branch_deleted_all(session=session)
    search = BaseSearchDto(page=page)
    pagination = PaginationDto(total_record=count)
    branches = await crud.find_branch_deleted_all(session=session, offset=search.offset, limit=search.limit)

    return BranchListResponse(list=branches, pagination=pagination)