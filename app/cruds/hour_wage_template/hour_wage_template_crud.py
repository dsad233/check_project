from datetime import datetime
from typing import List
from fastapi import Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.parts.hour_wage_template_model import HourWageTemplate, HourWageTemplateCreate, HourWageTemplateDelete, HourWageTemplateResponse, HourWageTemplateUpdate


async def create_hour_wage_template(
    *, branch_id: int, session: AsyncSession, hour_wage_template_create: HourWageTemplateCreate
) -> int:
    db_obj = HourWageTemplate(branch_id=branch_id, **hour_wage_template_create.model_dump())
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj.id

async def get_hour_wage_template_by_id(
    *, branch_id: int, hour_wage_template_id: int, session: AsyncSession
) -> HourWageTemplateResponse:
    stmt = select(HourWageTemplate).where(HourWageTemplate.branch_id == branch_id).where(HourWageTemplate.id == hour_wage_template_id)
    result = await session.execute(stmt)
    db_obj = result.scalar_one_or_none()
    return db_obj

async def get_hour_wage_template_list(
    *, branch_id: int, session: AsyncSession
) -> List[HourWageTemplateResponse]:
    stmt = select(HourWageTemplate).where(HourWageTemplate.branch_id == branch_id)
    result = await session.execute(stmt)
    return result.scalars().all()

async def update_hour_wage_template(
    *, branch_id: int, hour_wage_template_id: int, session: AsyncSession, hour_wage_template_update: HourWageTemplateUpdate
) -> int:
    
    update_data = hour_wage_template_update.model_dump(exclude_unset=True)

    update_stmt = (
        update(HourWageTemplate)
        .where(HourWageTemplate.branch_id == branch_id)
        .where(HourWageTemplate.id == hour_wage_template_id)
        .values(**update_data)
    )

    await session.execute(update_stmt)

    await session.commit()
    return hour_wage_template_id

async def delete_hour_wage_template(
    *, branch_id: int, hour_wage_template_id: int, session: AsyncSession, hour_wage_template: HourWageTemplate
) -> None:

    hour_wage_template.deleted_yn = "Y"
    hour_wage_template.updated_at = datetime.now()

    await session.commit()
