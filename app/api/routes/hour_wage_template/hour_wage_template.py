from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.cruds.hour_wage_template import hour_wage_template_crud
from app.cruds.users import users_crud
from app.exceptions.exceptions import ForbiddenError
from app.core.permissions.auth_utils import available_higher_than
from app.enums.users import Role
from app.middleware.tokenVerify import validate_token, get_current_user_id
from app.schemas.branches_schemas import HourWageTemplateRequest, HourWageTemplateResponse, HourWageTemplatesResponse
from app.models.parts.hour_wage_template_model import HourWageTemplate


router = APIRouter()

@router.get("/list", response_model=list[HourWageTemplateResponse], summary="시급 템플릿 목록 조회")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def get_hour_wage_template_list(*,
    branch_id: int,
    session: AsyncSession = Depends(get_db),
    context: Request
) -> list[HourWageTemplateResponse]:

    hour_wage_templates = await hour_wage_template_crud.find_all_by_branch_id(branch_id=branch_id, session=session)
    if not hour_wage_templates:
        return []
    return hour_wage_templates

@router.post("/create", response_model=HourWageTemplateResponse, summary="시급 템플릿 생성")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def create_hour_wage_template(*,
    branch_id: int,
    request: HourWageTemplateRequest,
    session: AsyncSession = Depends(get_db),
    context: Request
) -> HourWageTemplateResponse:

    hour_wage_template = await hour_wage_template_crud.create(branch_id=branch_id, request=HourWageTemplate(branch_id=branch_id, **request.model_dump()), session=session)
    return hour_wage_template

@router.patch("/{hour_wage_template_id}/update", response_model=bool, summary="시급 템플릿 수정")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def update_hour_wage_template(*,
    branch_id: int,
    hour_wage_template_id: int,
    request: HourWageTemplateRequest,
    session: AsyncSession = Depends(get_db),
    context: Request
) -> bool:

    return await hour_wage_template_crud.update(branch_id=branch_id, hour_wage_template_id=hour_wage_template_id, request=HourWageTemplate(branch_id=branch_id, **request.model_dump(exclude_unset=True)), session=session)


@router.delete("/{hour_wage_template_id}/delete", response_model=bool, summary="시급 템플릿 삭제")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def delete_hour_wage_template(*,
    branch_id: int,
    hour_wage_template_id: int,
    session: AsyncSession = Depends(get_db),
    context: Request
) -> bool:

    return await hour_wage_template_crud.delete(branch_id=branch_id, hour_wage_template_id=hour_wage_template_id, session=session)
