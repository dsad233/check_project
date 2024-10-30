import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.exceptions import ForbiddenError
from app.core.database import get_db
from app.cruds.personnel_record_categories import personnel_record_categories_crud
from app.cruds.users import users_crud
from app.middleware.tokenVerify import validate_token, get_current_user_id
from app.models.branches.personnel_record_categories_model import PersonnelRecordCategoryDto

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(validate_token)])

async def check_role(*, session: AsyncSession, current_user_id: int, branch_id: int):
    user = await users_crud.find_by_id(session=session, user_id=current_user_id)
    if user.role.strip() == "MSO 최고권한":
        pass
    elif user.role.strip() in ["최고관리자", "파트관리자", "통합관리자"]:
        if user.branch_id != branch_id:
            raise ForbiddenError(detail="다른 지점의 정보에 접근할 수 없습니다.")
    else:
        raise ForbiddenError(detail="권한이 없습니다.")

@router.get("", response_model=List[PersonnelRecordCategoryDto])
async def read_personnel_record_categories(
    *,
    branch_id: int,
    session: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) -> List[PersonnelRecordCategoryDto]:
    await check_role(session=session, current_user_id=current_user_id, branch_id=branch_id)
    
    categories = await personnel_record_categories_crud.find_all_by_branch_id(
        session=session, 
        branch_id=branch_id
    )
    return [PersonnelRecordCategoryDto.model_validate(category) for category in categories]

@router.post("", response_model=str, status_code=201)
async def create_personnel_record_category(
    *,
    branch_id: int,
    session: AsyncSession = Depends(get_db),
    data: PersonnelRecordCategoryDto,
    current_user_id: int = Depends(get_current_user_id)
) -> str:
    await check_role(session=session, current_user_id=current_user_id, branch_id=branch_id)
    
    category_id = await personnel_record_categories_crud.create(
        session=session, 
        branch_id=branch_id, 
        category_create=data
    )
    return f"{category_id}번 인사기록 카테고리가 생성되었습니다."

@router.patch("/{category_id}", response_model=str)
async def update_personnel_record_category(
    *,
    branch_id: int,
    category_id: int,
    session: AsyncSession = Depends(get_db),
    data: PersonnelRecordCategoryDto,
    current_user_id: int = Depends(get_current_user_id)
) -> str:
    """
    인사기록 카테고리를 수정합니다.
    
    - 수정할 카테고리 내용을 입력합니다.
    - 오류 발생 시 500 Internal Server Error를 반환합니다.
    """
    await check_role(session=session, current_user_id=current_user_id, branch_id=branch_id)
    
    await personnel_record_categories_crud.update(
        session=session, 
        branch_id=branch_id, 
        category_id=category_id, 
        category_update=data
    )
    return f"{category_id}번 인사기록 카테고리가 수정되었습니다."

@router.delete("/{category_id}", response_model=str)
async def delete_personnel_record_category(
    *,
    branch_id: int,
    category_id: int,
    session: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) -> str:
    await check_role(session=session, current_user_id=current_user_id, branch_id=branch_id)
    
    await personnel_record_categories_crud.delete(
        session=session, 
        branch_id=branch_id, 
        category_id=category_id
    )
    return f"{category_id}번 인사기록 카테고리가 삭제되었습니다."