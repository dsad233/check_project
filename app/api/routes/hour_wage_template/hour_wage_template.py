import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.cruds.hour_wage_template import hour_wage_template_crud
from app.cruds.users import users_crud
from app.exceptions.exceptions import ForbiddenError
from app.middleware.tokenVerify import validate_token, get_current_user_id
from app.models.parts.hour_wage_template_model import (
    HourWageTemplate,
    HourWageTemplateCreate,
    HourWageTemplateResponse,
    HourWageTemplateUpdate,
)

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

@router.get("/list", response_model=List[HourWageTemplateResponse])
async def get_hour_wage_template_list(
    branch_id: int,
    session: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) -> List[HourWageTemplateResponse]:
    
    await check_role(session=session, current_user_id=current_user_id, branch_id=branch_id)

    hour_wage_templates = await hour_wage_template_crud.find_all_by_branch_id(branch_id=branch_id, session=session)
    if not hour_wage_templates:
        return []
    return hour_wage_templates

@router.post("/create", response_model=str)
async def create_hour_wage_template(
    branch_id: int,
    hour_wage_template_create: HourWageTemplateCreate,
    session: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) -> str:
    
    await check_role(session=session, current_user_id=current_user_id, branch_id=branch_id)

    create_in = HourWageTemplate(branch_id=branch_id, **hour_wage_template_create.model_dump())
    hour_wage_template_id = await hour_wage_template_crud.create(branch_id=branch_id, hour_wage_template_create=create_in, session=session)
    return f"{hour_wage_template_id}번 시급 템플릿이 생성되었습니다."

@router.patch("/{hour_wage_template_id}/update", response_model=str)
async def update_hour_wage_template(
    branch_id: int,
    hour_wage_template_id: int,
    hour_wage_template_update: HourWageTemplateUpdate,
    session: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) -> str:
    
    await check_role(session=session, current_user_id=current_user_id, branch_id=branch_id)

    update_in = HourWageTemplate(branch_id=branch_id, **hour_wage_template_update.model_dump(exclude_unset=True))
    await hour_wage_template_crud.update(branch_id=branch_id, hour_wage_template_id=hour_wage_template_id, hour_wage_template_update=update_in, session=session)
    return f"{hour_wage_template_id}번 시급 템플릿이 수정되었습니다."

@router.delete("/{hour_wage_template_id}/delete", response_model=str)
async def delete_hour_wage_template(
    branch_id: int,
    hour_wage_template_id: int,
    session: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) -> str:
    
    await check_role(session=session, current_user_id=current_user_id, branch_id=branch_id)

    await hour_wage_template_crud.delete(branch_id=branch_id, hour_wage_template_id=hour_wage_template_id, session=session)
    return f"{hour_wage_template_id}번 시급 템플릿이 삭제되었습니다."