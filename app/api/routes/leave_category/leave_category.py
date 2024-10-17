import logging
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dto.pagination_dto import PaginationDto
from app.common.dto.search_dto import BaseSearchDto
from app.core.database import get_db
from app.cruds.parts import parts_crud
from app.cruds.leave_categories import leave_categories_crud, leave_excluded_parts_crud
from app.middleware.tokenVerify import validate_token
from app.models.branches.leave_categories_model import (
    LeaveCategoryCreate,
    LeaveCategoryListResponse,
    LeaveCategoryResponse,
    LeaveCategoryUpdate
)

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(validate_token)])

class ExcludedPartIdAndPartName(BaseModel):
    id: int
    part_name: str

class LeaveCategoryWithExcludedPartsResponse(BaseModel):
    leave_category: LeaveCategoryResponse
    excluded_parts: list[ExcludedPartIdAndPartName]

class LeaveCreateWithExcludedPartIds(BaseModel):
    create_leave_category: LeaveCategoryCreate
    excluded_part_ids: Optional[list[int]] = None

class LeaveUpdateWithExcludedPartIds(BaseModel):
    update_leave_category: LeaveCategoryUpdate
    excluded_part_ids: Optional[list[int]] = None

    
@router.get("/list", response_model=List[LeaveCategoryWithExcludedPartsResponse])
async def read_leave_categories(
    *,
    branch_id: int,
    session: AsyncSession = Depends(get_db)
) -> List[LeaveCategoryWithExcludedPartsResponse]:
    try:
        leave_categories = await leave_categories_crud.find_leave_category_all(
            session=session, branch_id=branch_id
        )
        result = []
        # 제외 부서 id와 이름 추가
        for leave_category in leave_categories:
            excluded_parts = await leave_excluded_parts_crud.get_all_by_leave_category_id(
                session=session, leave_category_id=leave_category.id
            )
            excluded_parts_data = [
                ExcludedPartIdAndPartName(
                    id=excluded_part.id,
                    part_name=await parts_crud.get_name_by_branch_id_and_part_id(
                        session=session, branch_id=branch_id, part_id=excluded_part.part_id
                    )
                )
                for excluded_part in excluded_parts
            ]
            result.append(LeaveCategoryWithExcludedPartsResponse(
                excluded_parts=excluded_parts_data,
                leave_category=LeaveCategoryResponse.model_validate(leave_category)
            ))
        return result
    except Exception as e:
        logger.error(f"Error occurred while getting leave category list: {e}")
        raise HTTPException(status_code=500, detail=f"Error occurred while getting leave category list: {e}")


@router.post("/create", response_model=str, status_code=201)
async def create_leave_category(
    *,
    branch_id: int,
    session: AsyncSession = Depends(get_db),
    data: LeaveCreateWithExcludedPartIds
) -> str:
    try:
        leave_category_id = await leave_categories_crud.create_leave_category(
            session=session, branch_id=branch_id, leave_category_create=data.create_leave_category
        )
        if data.excluded_part_ids:
            for part_id in data.excluded_part_ids:
                await leave_excluded_parts_crud.create(
                    session=session, leave_category_id=leave_category_id, part_id=part_id
                )
        return f"{leave_category_id}번 휴가 카테고리가 생성되었습니다."
    except Exception as e:
        logger.error(f"Error occurred while creating leave category: {e}")
        raise HTTPException(status_code=500, detail=f"Error occurred while creating leave category: {e}")
    

@router.patch("/{leave_category_id}/update", response_model=str)
async def update_leave_category(
    *,
    branch_id: int,
    leave_category_id: int,
    session: AsyncSession = Depends(get_db),
    data: LeaveUpdateWithExcludedPartIds
) -> str:
    try:
        await leave_categories_crud.update_leave_category(
            session=session, branch_id=branch_id, leave_category_id=leave_category_id, leave_category_update=data.update_leave_category
        )
        if data.excluded_part_ids:
            for excluded_part_id in data.excluded_part_ids:
                await leave_excluded_parts_crud.delete(
                    session=session, leave_excluded_part_id=excluded_part_id
                )
        return f"{data.leave_category_update.name} 휴가 카테고리가 수정되었습니다."
    except Exception as e:
        logger.error(f"Error occurred while updating leave category: {e}")
        raise HTTPException(status_code=500, detail=f"Error occurred while updating leave category: {e}")


@router.delete("/{leave_category_id}/delete", response_model=str)
async def delete_leave_category(
    *,
    branch_id: int,
    leave_category_id: int,
    session: AsyncSession = Depends(get_db)
) -> str:
    try:
        await leave_categories_crud.delete_leave_category(
            session=session, branch_id=branch_id, leave_category_id=leave_category_id
        )
        return f"{leave_category_id}번 휴가 카테고리가 삭제되었습니다."
    except Exception as e:
        logger.error(f"Error occurred while deleting leave category: {e}")
        raise HTTPException(status_code=500, detail=f"Error occurred while deleting leave category: {e}")