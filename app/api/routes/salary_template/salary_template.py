from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.exceptions import ForbiddenError, NotFoundError, BadRequestError
from app.common.dto.pagination_dto import PaginationDto
from app.common.dto.search_dto import BaseSearchDto
from app.core.database import get_db
from app.cruds.salary_template import salary_template_crud
from app.service import salary_template_service
from app.schemas.salary_template_schemas import SalaryTemplateRequest, SalaryTemplateResponse, SalaryTemplatesResponse
from app.middleware.tokenVerify import validate_token, get_current_user_id
from app.models.branches.salary_template_model import SalaryTemplate
from app.core.permissions.auth_utils import available_higher_than
from app.enums.users import Role


router = APIRouter()

@router.get("/list", response_model=SalaryTemplatesResponse, summary="급여 템플릿 목록 조회")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def get_salary_templates(
    *,
    context: Request,
    branch_id: int,
    session: AsyncSession = Depends(get_db),
    request: BaseSearchDto = Depends(BaseSearchDto)
) -> SalaryTemplatesResponse:
    return await salary_template_service.get_all_salary_template_and_allowance_policy(session=session, branch_id=branch_id, request=request)


@router.post("/create", response_model=SalaryTemplateResponse, summary="급여 템플릿 생성")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def create_salary_template(
    *,
    branch_id: int,
    session: AsyncSession = Depends(get_db),
    request: SalaryTemplateRequest,
    context: Request
) -> SalaryTemplateResponse: 
    
    return await salary_template_service.create_salary_template(session=session, branch_id=branch_id, request=request)

    
@router.patch("/{salary_template_id}/update", response_model=bool, summary="급여 템플릿 수정")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def update_salary_template(
    *,
    branch_id: int,
    salary_template_id: int,
    session: AsyncSession = Depends(get_db),
    request: SalaryTemplateRequest,
    context: Request
) -> bool:
    
    return await salary_template_service.update_salary_template(session=session, branch_id=branch_id, salary_template_id=salary_template_id, request=request)

@router.delete("/{salary_template_id}/delete", response_model=bool, summary="급여 템플릿 삭제")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def delete_salary_template(
    *,
    branch_id: int,
    salary_template_id: int,
    session: AsyncSession = Depends(get_db),
    context: Request
) -> bool:
    
    return await salary_template_service.delete_salary_template(session=session, branch_id=branch_id, salary_template_id=salary_template_id)
