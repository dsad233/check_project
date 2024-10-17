import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.cruds.hour_wage_template import hour_wage_template_crud
from app.middleware.tokenVerify import validate_token
from app.models.parts.hour_wage_template_model import (
    HourWageTemplateCreate,
    HourWageTemplateDelete,
    HourWageTemplateResponse,
    HourWageTemplateUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(validate_token)])

@router.get("")
async def get_hour_wage_template_list(
    branch_id: int,
    session: AsyncSession = Depends(get_db)
) -> List[HourWageTemplateResponse]:
    try:
        return await hour_wage_template_crud.get_hour_wage_template_list(branch_id=branch_id, session=session)
    except Exception as e:
        logger.error(f"Error occurred while getting hour wage template list: {e}")
        raise HTTPException(status_code=500, detail=f"Error occurred while getting hour wage template list: {e}")

@router.post("")
async def create_hour_wage_template(
    branch_id: int,
    hour_wage_template_create: HourWageTemplateCreate,
    session: AsyncSession = Depends(get_db)
) -> str:
    try:
        hour_wage_template_id = await hour_wage_template_crud.create_hour_wage_template(branch_id=branch_id, hour_wage_template_create=hour_wage_template_create, session=session)
        return f"{hour_wage_template_id}번 시급 템플릿이 생성되었습니다."
    except Exception as e:
        logger.error(f"Error occurred while creating hour wage template: {e}")
        raise HTTPException(status_code=500, detail=f"Error occurred while creating hour wage template: {e}")

@router.put("/{hour_wage_template_id}")
async def update_hour_wage_template(
    branch_id: int,
    hour_wage_template_id: int,
    hour_wage_template_update: HourWageTemplateUpdate,
    session: AsyncSession = Depends(get_db)
) -> str:
    try:
        await hour_wage_template_crud.update_hour_wage_template(branch_id=branch_id, hour_wage_template_id=hour_wage_template_id, hour_wage_template_update=hour_wage_template_update, session=session)
        return f"{hour_wage_template_id}번 시급 템플릿이 수정되었습니다."
    except Exception as e:
        logger.error(f"Error occurred while updating hour wage template: {e}")
        raise HTTPException(status_code=500, detail=f"Error occurred while updating hour wage template: {e}")

@router.delete("/{hour_wage_template_id}", status_code=204)
async def delete_hour_wage_template(
    branch_id: int,
    hour_wage_template_id: int,
    session: AsyncSession = Depends(get_db)
) -> None:
    try:
        await hour_wage_template_crud.delete_hour_wage_template(branch_id=branch_id, hour_wage_template_id=hour_wage_template_id, session=session)
    except Exception as e:
        logger.error(f"Error occurred while deleting hour wage template: {e}")
        raise HTTPException(status_code=500, detail=f"Error occurred while deleting hour wage template: {e}")
