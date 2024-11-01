from typing import List, Optional
from fastapi import Depends
from datetime import datetime
from sqlalchemy import func, select, exists, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from app.common.dto.search_dto import BaseSearchDto
from app.models.branches.salary_template_model import SalaryTemplate
from app.exceptions.exceptions import NotFoundError, BadRequestError
from sqlalchemy.orm import selectinload


async def find_all_by_branch_id(*, session: AsyncSession, branch_id: int) -> list[SalaryTemplate]:
    stmt = (
        select(SalaryTemplate).options(selectinload(SalaryTemplate.part)).where(SalaryTemplate.branch_id == branch_id).where(SalaryTemplate.deleted_yn == "N")
    )
    result = await session.execute(stmt)
    return result.scalars().all()

async def find_salary_templates(*, session: AsyncSession, branch_id: int, request: BaseSearchDto) -> list[SalaryTemplate]:
    stmt = (
        select(SalaryTemplate).options(selectinload(SalaryTemplate.part)).where(
            SalaryTemplate.branch_id == branch_id
        ).where(
            SalaryTemplate.deleted_yn == "N"
        ).order_by(
            SalaryTemplate.created_at.desc()
        ).offset(request.offset).limit(request.record_size)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def find_by_id(*, session: AsyncSession, id: int) -> Optional[SalaryTemplate]:
    stmt = (
        select(SalaryTemplate).options(selectinload(SalaryTemplate.part)).where(SalaryTemplate.id == id).where(SalaryTemplate.deleted_yn == "N")
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def find_by_branch_id_and_name(*, session: AsyncSession, branch_id: int, name: str) -> Optional[SalaryTemplate]:
    stmt = (
        select(SalaryTemplate).where(SalaryTemplate.branch_id == branch_id).where(SalaryTemplate.name == name).where(SalaryTemplate.deleted_yn == "N")
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def create(*, session: AsyncSession, request: SalaryTemplate, branch_id: int) -> SalaryTemplate:

    session.add(request)
    await session.commit()
    await session.refresh(request)
    return request

async def update(*, session: AsyncSession, request: SalaryTemplate, branch_id: int, id: int, old: SalaryTemplate) -> bool:
    
    # 변경된 필드만 업데이트
    changed_fields = {}
    for column in SalaryTemplate.__table__.columns:
        if column.name not in ['id', 'branch_id', 'created_at', 'updated_at', 'deleted_yn']:
            new_value = getattr(request, column.name)
            if new_value is not None and getattr(old, column.name) != new_value:
                changed_fields[column.name] = new_value
    if changed_fields:
        # 변경된 필드가 있을 경우에만 업데이트 수행
        stmt = sa_update(SalaryTemplate).where(SalaryTemplate.branch_id == branch_id).where(SalaryTemplate.id == id).values(**changed_fields)
        await session.execute(stmt)
        old.updated_at = datetime.now()
        await session.commit()
        await session.refresh(old)
    else:
        pass
    return True


async def delete(*, session: AsyncSession, branch_id: int, id: int) -> bool:
    
    await session.execute(
            sa_update(SalaryTemplate)
            .where(SalaryTemplate.id == id)
            .values(
                deleted_yn="Y",
                updated_at=datetime.now()
            )
        )
    await session.commit()
    return True

async def count_all_by_branch_id(*, session: AsyncSession, branch_id: int) -> int:
    stmt = select(func.count(SalaryTemplate.id)).where(SalaryTemplate.branch_id == branch_id).where(SalaryTemplate.deleted_yn == "N")
    result = await session.execute(stmt)
    return result.scalar_one()