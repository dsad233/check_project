from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.cruds.hour_wage_template import hour_wage_template_crud
from app.cruds.users import users_crud
from app.service import branch_service
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

    return await branch_service.get_hour_wage_templates(session=session, branch_id=branch_id)

@router.post("/create", response_model=HourWageTemplateResponse, summary="시급 템플릿 생성")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def create_hour_wage_template(*,
    branch_id: int,
    request: HourWageTemplateRequest,
    session: AsyncSession = Depends(get_db),
    context: Request
) -> HourWageTemplateResponse:

    return await branch_service.create_hour_wage_template(session=session, branch_id=branch_id, request=request)

@router.patch("/{hour_wage_template_id}/update", response_model=bool, summary="시급 템플릿 수정")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def update_hour_wage_template(*,
    branch_id: int,
    hour_wage_template_id: int,
    request: HourWageTemplateRequest,
    session: AsyncSession = Depends(get_db),
    context: Request
) -> bool:

    return await branch_service.update_hour_wage_template(session=session, branch_id=branch_id, hour_wage_template_id=hour_wage_template_id, request=request)


@router.delete("/{hour_wage_template_id}/delete", response_model=bool, summary="시급 템플릿 삭제")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def delete_hour_wage_template(*,
    branch_id: int,
    hour_wage_template_id: int,
    session: AsyncSession = Depends(get_db),
    context: Request
) -> bool:

    return await branch_service.delete_hour_wage_template(session=session, branch_id=branch_id, hour_wage_template_id=hour_wage_template_id)