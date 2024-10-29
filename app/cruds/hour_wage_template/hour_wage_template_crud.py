import logging
from datetime import datetime
from typing import List, Optional
from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, NoResultFound
from sqlalchemy import select, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.parts.hour_wage_template_model import HourWageTemplate
from app.exceptions.exceptions import BadRequestError, NotFoundError

logger = logging.getLogger(__name__)

async def create(
    *, branch_id: int, session: AsyncSession, hour_wage_template_create: HourWageTemplate
) -> int:
    hour_wage_template = await find_by_name_and_branch_id(session=session, branch_id=branch_id, name=hour_wage_template_create.name)
    if hour_wage_template:
        raise BadRequestError(f"{branch_id}번 지점의 시간 임금 템플릿 이름 {hour_wage_template_create.name}이 이미 존재합니다.")
    session.add(hour_wage_template_create)
    await session.commit()
    await session.refresh(hour_wage_template_create)
    return hour_wage_template_create.id

async def find_by_name_and_branch_id(
    *, session: AsyncSession, branch_id: int, name: str
) -> Optional[HourWageTemplate]:
    
    stmt = select(HourWageTemplate).where(HourWageTemplate.branch_id == branch_id).where(HourWageTemplate.name == name).where(HourWageTemplate.deleted_yn == "N")
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
    

async def find_by_id(
    *, branch_id: int, hour_wage_template_id: int, session: AsyncSession
) -> Optional[HourWageTemplate]:
        
    stmt = select(HourWageTemplate).where(HourWageTemplate.branch_id == branch_id).where(HourWageTemplate.id == hour_wage_template_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def find_all_by_branch_id(
    *, branch_id: int, session: AsyncSession
) -> List[HourWageTemplate]:
    
    stmt = select(HourWageTemplate).where(HourWageTemplate.branch_id == branch_id).where(HourWageTemplate.deleted_yn == "N")
    result = await session.execute(stmt)
    return result.scalars().all()

async def update(
    *, branch_id: int, hour_wage_template_id: int, session: AsyncSession, hour_wage_template_update: HourWageTemplate
) -> int:
        
    # 기존 정책 조회
    hour_wage_template = await find_by_id(branch_id=branch_id, hour_wage_template_id=hour_wage_template_id, session=session)

    if hour_wage_template is None:
        raise NotFoundError(f"{branch_id}번 지점의 {hour_wage_template_id}번 시간 임금 템플릿이 존재하지 않습니다.")

    # 변경된 필드만 업데이트
    changed_fields = {}
    for column in HourWageTemplate.__table__.columns:
        if column.name not in ['id', 'branch_id', 'created_at', 'updated_at', 'deleted_yn']:
            new_value = getattr(hour_wage_template_update, column.name)
            if column.name == 'part_id' and new_value is None:
                changed_fields[column.name] = None
            if new_value is not None and getattr(hour_wage_template, column.name) != new_value:
                changed_fields[column.name] = new_value

    if changed_fields:
        # 변경된 필드가 있을 경우에만 업데이트 수행
        stmt = sa_update(HourWageTemplate).where(HourWageTemplate.branch_id == branch_id).where(HourWageTemplate.id == hour_wage_template_id).values(**changed_fields)
        await session.execute(stmt)
        hour_wage_template.updated_at = datetime.now()
        await session.commit()
        await session.refresh(hour_wage_template)
    else:
        pass

    return hour_wage_template

async def delete(
    *, branch_id: int, hour_wage_template_id: int, session: AsyncSession
) -> None:
        
    hour_wage_template = await find_by_id(branch_id=branch_id, hour_wage_template_id=hour_wage_template_id, session=session)
    if hour_wage_template is None:
        raise NotFoundError(f"{branch_id}번 지점의 {hour_wage_template_id}번 시간 임금 템플릿을 찾을 수 없습니다.")
    hour_wage_template.deleted_yn = "Y"
    hour_wage_template.updated_at = datetime.now()

    await session.commit()