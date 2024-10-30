import logging
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.exceptions import ForbiddenError, NotFoundError, BadRequestError
from app.common.dto.pagination_dto import PaginationDto
from app.common.dto.search_dto import BaseSearchDto
from app.core.database import get_db
from app.cruds.salary_template import salary_template_crud
from app.service import branch_service
from app.schemas.branches_schemas import SalaryTemplateRequest, SalaryTemplateResponse, SalaryTemplatesResponse
from app.middleware.tokenVerify import validate_token, get_current_user_id
from app.models.branches.salary_template_model import SalaryTemplate
from app.core.permissions.auth_utils import available_higher_than
from app.enums.users import Role


router = APIRouter(dependencies=[Depends(validate_token)])

@router.get("/list", response_model=SalaryTemplatesResponse)
async def get_salary_templates(
    *,
    branch_id: int,
    session: AsyncSession = Depends(get_db),
    request: BaseSearchDto = Depends(BaseSearchDto)
) -> SalaryTemplatesResponse:
    return await branch_service.get_all_salary_template_and_allowance_policy(session=session, branch_id=branch_id, request=request)


@router.post("/create", response_model=SalaryTemplateResponse)
@available_higher_than(Role.INTEGRATED_ADMIN)
async def create_salary_template(
    *,
    branch_id: int,
    session: AsyncSession = Depends(get_db),
    request: SalaryTemplateRequest,
    context: Request
) -> SalaryTemplateResponse: 
    salary_template = await salary_template_crud.find_by_branch_id_and_name(session=session, branch_id=branch_id, name=request.name)
    if salary_template:
        raise BadRequestError(detail=f"{request.name}이미 존재하는 급여 템플릿입니다.")
    
    salary_template = await salary_template_crud.create(session=session, request=SalaryTemplate(branch_id=branch_id, **request.model_dump(exclude_none=True)), branch_id=branch_id)
    return salary_template
    
    
@router.patch("/{salary_template_id}/update", response_model=bool)
@available_higher_than(Role.INTEGRATED_ADMIN)
async def update_salary_template(
    *,
    branch_id: int,
    salary_template_id: int,
    session: AsyncSession = Depends(get_db),
    request: SalaryTemplateRequest,
    context: Request
) -> bool:
    
    salary_template = await salary_template_crud.find_by_id(session=session, id=salary_template_id)
    if not salary_template:
        raise NotFoundError(detail=f"{salary_template_id}번 급여 템플릿이 존재하지 않습니다.")
    
    return await salary_template_crud.update(session=session, branch_id=branch_id, request=SalaryTemplate(branch_id=branch_id, **request.model_dump(exclude_none=True)), id=salary_template_id)


@router.delete("/{salary_template_id}/delete", response_model=bool)
@available_higher_than(Role.INTEGRATED_ADMIN)
async def delete_salary_template(
    *,
    branch_id: int,
    salary_template_id: int,
    session: AsyncSession = Depends(get_db),
    context: Request
) -> bool:
    salary_template = await salary_template_crud.find_by_id(session=session, id=salary_template_id)
    if not salary_template:
        raise NotFoundError(detail=f"{salary_template_id}번 급여 템플릿이 존재하지 않습니다.")
    
    return await salary_template_crud.delete(session=session, id=salary_template_id, branch_id=branch_id)
