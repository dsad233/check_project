import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dto.pagination_dto import PaginationDto
from app.common.dto.search_dto import BaseSearchDto
from app.core.database import get_db
from app.cruds.branches import branches_crud
from app.cruds.branches.policies import holiday_work_crud, overtime_crud, work_crud, auto_overtime_crud, allowance_crud
from app.middleware.tokenVerify import validate_token
from app.models.branches.branches_model import (
    BranchCreate,
    BranchDelete,
    BranchListResponse,
    BranchResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(validate_token)])
# router = APIRouter()


@router.get("/", response_model=BranchListResponse)
async def read_branches(
    *, session: AsyncSession = Depends(get_db), search: BaseSearchDto = Depends()
) -> BranchListResponse:
    count = await branches_crud.count_branch_all(session=session)
    pagination = PaginationDto(total_record=count)
    branches = await branches_crud.find_branch_all(
        session=session, offset=search.offset, limit=search.record_size
    )

    return BranchListResponse(list=branches, pagination=pagination)


@router.post("/", response_model=str, status_code=201)
async def create_branch(
    *, session: AsyncSession = Depends(get_db), branch_in: BranchCreate
) -> str:
    branch = await branches_crud.create_branch(session=session, branch_create=branch_in)
    branch_id = branch.id
    # 정책 생성
    await holiday_work_crud.create_holiday_work_policies(session=session, branch_id=branch_id)
    await overtime_crud.create_overtime_policies(session=session, branch_id=branch_id)
    await work_crud.create_work_policies(session=session, branch_id=branch_id)
    await auto_overtime_crud.create_auto_overtime_policies(session=session, branch_id=branch_id)
    await allowance_crud.create_allowance_policies(session=session, branch_id=branch_id)
    return f"{branch_id}번 지점이 생성되었습니다."


@router.get("/{branch_id}", response_model=BranchResponse)
async def read_branch(
    *, session: AsyncSession = Depends(get_db), branch_id: int
) -> BranchResponse:
    branch = await branches_crud.find_branch_by_id(session=session, branch_id=branch_id)
    if branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch


@router.delete("/{branch_id}", status_code=204)
async def delete_branch(
    *, session: AsyncSession = Depends(get_db), branch_id: int
) -> None:
    branch = await branches_crud.find_branch_by_id(session=session, branch_id=branch_id)
    if branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")
    await branches_crud.delete_branch(session=session, branch=branch)


@router.get("/deleted", response_model=BranchListResponse)
async def read_deleted_branches(
    *, session: AsyncSession = Depends(get_db), search: BaseSearchDto = Depends()
) -> BranchListResponse:
    count = await branches_crud.count_branch_deleted_all(session=session)
    pagination = PaginationDto(total_record=count)
    branches = await branches_crud.find_branch_deleted_all(
        session=session, offset=search.offset, limit=search.record_size
    )

    return BranchListResponse(list=branches, pagination=pagination)