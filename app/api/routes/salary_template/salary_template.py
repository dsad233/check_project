import logging
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.exceptions import ForbiddenError, NotFoundError, BadRequestError
from app.common.dto.pagination_dto import PaginationDto
from app.common.dto.search_dto import BaseSearchDto
from app.core.database import get_db
from app.cruds.salary_template import salary_template_crud
from app.service import salary_template_service
from app.middleware.tokenVerify import validate_token, get_current_user_id
from app.models.branches.salary_template_model import SalaryTemplate, SalaryTemplateDto


router = APIRouter(dependencies=[Depends(validate_token)])

@router.get("/list", response_model=List[SalaryTemplateDto])
async def get_salary_templates(
    *,
    branch_id: int,
    session: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) -> List[SalaryTemplateDto]:
    return await salary_template_service.get_all_salary_template_and_allowance_policy(session=session, branch_id=branch_id)


@router.post("/create", response_model=str)
async def create_salary_template(
    *,
    branch_id: int,
    session: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    salary_template_create: SalaryTemplateDto
) -> str: 
    salary_template = await salary_template_crud.find_by_branch_id_and_name(session=session, branch_id=branch_id, name=salary_template_create.name)
    if salary_template:
        raise BadRequestError(detail=f"{salary_template_create.name}이미 존재하는 급여 템플릿입니다.")
    
    salary_template_create_in = SalaryTemplate(branch_id=branch_id, **salary_template_create.model_dump(exclude_none=True))
    salary_template_id = await salary_template_crud.create(session=session, salary_template_create=salary_template_create_in, branch_id=branch_id)
    return f"{salary_template_id}번 급여 템플릿이 생성되었습니다."
    
    
@router.patch("/{salary_template_id}/update", response_model=str)
async def update_salary_template(
    *,
    branch_id: int,
    salary_template_id: int,
    session: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    salary_template_update: SalaryTemplateDto
) -> str:
    salary_template = await salary_template_crud.find_by_id(session=session, id=salary_template_id)
    if not salary_template:
        raise NotFoundError(detail=f"{salary_template_id}번 급여 템플릿이 존재하지 않습니다.")
    
    salary_template_update_in = SalaryTemplate(branch_id=branch_id, **salary_template_update.model_dump(exclude_none=True))
    salary_template = await salary_template_crud.update(session=session, branch_id=branch_id, salary_template_update=salary_template_update_in, id=salary_template_id)
    return f"{salary_template_id}번 급여 템플릿이 수정되었습니다."


@router.delete("/{salary_template_id}/delete", response_model=str)
async def delete_salary_template(
    *,
    branch_id: int,
    salary_template_id: int,
    session: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
) -> str:
    salary_template = await salary_template_crud.find_by_id(session=session, id=salary_template_id)
    if not salary_template:
        raise NotFoundError(detail=f"{salary_template_id}번 급여 템플릿이 존재하지 않습니다.")
    
    await salary_template_crud.delete(session=session, id=salary_template_id, branch_id=branch_id)
    return f"{salary_template_id}번 급여 템플릿이 삭제되었습니다."