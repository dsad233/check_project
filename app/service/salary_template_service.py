from app.cruds.salary_template import salary_template_crud
from app.cruds.branches import branches_crud
from app.schemas.salary_template_schemas import SalaryTemplateResponse, SalaryTemplatesResponse, SalaryTemplateRequest
from app.common.dto.pagination_dto import PaginationDto
from app.common.dto.search_dto import BaseSearchDto
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.branches.salary_template_model import SalaryTemplate
from app.exceptions.exceptions import BadRequestError, NotFoundError


async def get_all_salary_template_and_allowance_policy(
        *, 
        session: AsyncSession, 
        branch_id: int, 
        request: BaseSearchDto
) -> SalaryTemplatesResponse:
    """급여 템플릿 조회"""
    salary_templates = await salary_template_crud.find_salary_templates(session=session, branch_id=branch_id, request=request)
    if not salary_templates:
        return SalaryTemplatesResponse(data=[], pagination=PaginationDto(total_record=0))
    total_count = await salary_template_crud.count_all_by_branch_id(session=session, branch_id=branch_id)
    branch = await branches_crud.find_by_id_with_policies(session=session, branch_id=branch_id)

    data = [SalaryTemplateResponse(
        **SalaryTemplateResponse.model_validate(salary_template).model_dump(exclude_none=True),
        part_name=salary_template.part.name,
        job_allowance=branch.allowance_policies.job_allowance,
        meal_allowance=branch.allowance_policies.meal_allowance, 
        holiday_allowance=branch.allowance_policies.doctor_holiday_work_pay if salary_template.part.is_doctor else branch.allowance_policies.common_holiday_work_pay
        ) for salary_template in salary_templates]

    return SalaryTemplatesResponse(data=data, pagination=PaginationDto(total_record=total_count))


async def create_salary_template(*, session: AsyncSession, branch_id: int, request: SalaryTemplateRequest) -> SalaryTemplateResponse:
    """급여 템플릿 생성"""
    salary_template = await salary_template_crud.find_by_branch_id_and_name(session=session, branch_id=branch_id, name=request.name)
    if salary_template:
        raise BadRequestError(detail=f"{request.name}은 이미 존재하는 급여 템플릿입니다.")
    
    return await salary_template_crud.create(session=session, request=SalaryTemplate(branch_id=branch_id, **request.model_dump(exclude_none=True)), branch_id=branch_id)


async def update_salary_template(*, session: AsyncSession, branch_id: int, salary_template_id: int, request: SalaryTemplateRequest) -> bool:
    """급여 템플릿 수정"""
    salary_template = await salary_template_crud.find_by_id(session=session, id=salary_template_id)
    if not salary_template:
        raise NotFoundError(detail=f"{salary_template_id}번 급여 템플릿이 존재하지 않습니다.")
    
    return await salary_template_crud.update(session=session, branch_id=branch_id, request=SalaryTemplate(branch_id=branch_id, **request.model_dump(exclude_none=True)), id=salary_template_id, old=salary_template)


async def delete_salary_template(*, session: AsyncSession, branch_id: int, salary_template_id: int) -> bool:
    """급여 템플릿 삭제"""
    salary_template = await salary_template_crud.find_by_id(session=session, id=salary_template_id)
    if not salary_template:
        raise NotFoundError(detail=f"{salary_template_id}번 급여 템플릿이 존재하지 않습니다.")
    
    return await salary_template_crud.delete(session=session, id=salary_template_id, branch_id=branch_id)