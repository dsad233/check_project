from app.schemas.hour_wage_template_schemas import HourWageTemplateRequest, HourWageTemplateResponse
from app.models.parts.hour_wage_template_model import HourWageTemplate
from app.cruds.hour_wage_template import hour_wage_template_crud
from app.exceptions.exceptions import NotFoundError, BadRequestError
from sqlalchemy.ext.asyncio import AsyncSession


async def get_hour_wage_templates(*, session: AsyncSession, branch_id: int) -> list[HourWageTemplateResponse]:
    """시급 임금 템플릿 조회"""
    hour_wage_templates = await hour_wage_template_crud.find_all_by_branch_id(branch_id=branch_id, session=session)
    if not hour_wage_templates:
        return []
    return hour_wage_templates


async def create_hour_wage_template(*, session: AsyncSession, branch_id: int, request: HourWageTemplateRequest) -> HourWageTemplateResponse:
    """시급 임금 템플릿 생성"""
    hour_wage_template = await hour_wage_template_crud.find_by_name_and_branch_id(session=session, branch_id=branch_id, name=request.name)
    if hour_wage_template:
        raise BadRequestError(f"{branch_id}번 지점의 시간 임금 템플릿 이름 {request.name}이 이미 존재합니다.")
    
    
    return await hour_wage_template_crud.create(branch_id=branch_id, request=HourWageTemplate(branch_id=branch_id, **request.model_dump()), session=session)


async def update_hour_wage_template(*, session: AsyncSession, branch_id: int, hour_wage_template_id: int, request: HourWageTemplateRequest) -> bool:
    """시급 임금 템플릿 수정"""
    hour_wage_template = await hour_wage_template_crud.find_by_id(branch_id=branch_id, hour_wage_template_id=hour_wage_template_id, session=session)

    if hour_wage_template is None:
        raise NotFoundError(f"{branch_id}번 지점의 {hour_wage_template_id}번 시간 임금 템플릿이 존재하지 않습니다.")
    
    if hour_wage_template.name != request.name:
        duplicate_hour_wage_template = await hour_wage_template_crud.find_by_name_and_branch_id(session=session, branch_id=branch_id, name=request.name)
        if duplicate_hour_wage_template is not None:
            raise BadRequestError(detail=f"{request.name}은(는) 이미 존재하는 시간 임금 템플릿입니다.")
    
    return await hour_wage_template_crud.update(branch_id=branch_id, hour_wage_template_id=hour_wage_template_id, request=HourWageTemplate(branch_id=branch_id, **request.model_dump(exclude_unset=True)), session=session, old=hour_wage_template)


async def delete_hour_wage_template(*, session: AsyncSession, branch_id: int, hour_wage_template_id: int) -> bool:
    """시급 임금 템플릿 삭제"""
    hour_wage_template = await hour_wage_template_crud.find_by_id(branch_id=branch_id, hour_wage_template_id=hour_wage_template_id, session=session)
    if hour_wage_template is None:
        raise NotFoundError(f"{branch_id}번 지점의 {hour_wage_template_id}번 시간 임금 템플릿을 찾을 수 없습니다.")
    return await hour_wage_template_crud.delete(branch_id=branch_id, hour_wage_template_id=hour_wage_template_id, session=session)