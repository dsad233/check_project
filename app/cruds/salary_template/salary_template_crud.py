from typing import List, Optional
from fastapi import Depends
from datetime import datetime
from sqlalchemy import func, select, exists, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from app.common.dto.search_dto import BaseSearchDto
from app.models.branches.salary_template_model import SalaryTemplate
from app.exceptions.exceptions import NotFoundError, BadRequestError


async def find_all_by_branch_id(*, session: AsyncSession, branch_id: int) -> List[SalaryTemplate]:
    stmt = (
        select(SalaryTemplate).where(SalaryTemplate.branch_id == branch_id).where(SalaryTemplate.deleted_yn == "N")
    )
    result = await session.execute(stmt)
    return result.scalars().all()

async def find_by_id(*, session: AsyncSession, id: int) -> Optional[SalaryTemplate]:
    stmt = (
        select(SalaryTemplate).where(SalaryTemplate.id == id).where(SalaryTemplate.deleted_yn == "N")
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def find_by_branch_id_and_name(*, session: AsyncSession, branch_id: int, name: str) -> Optional[SalaryTemplate]:
    stmt = (
        select(SalaryTemplate).where(SalaryTemplate.branch_id == branch_id).where(SalaryTemplate.name == name).where(SalaryTemplate.deleted_yn == "N")
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def create(*, session: AsyncSession, salary_template_create: SalaryTemplate, branch_id: int) -> int:
    # salary_template = await find_by_branch_id_and_name(session=session, branch_id=branch_id, name=salary_template_create.name)
    # if salary_template is not None:
    #     raise BadRequestError(f"이미 존재하는 템플릿입니다.")
    session.add(salary_template_create)
    await session.commit()
    await session.refresh(salary_template_create)
    return salary_template_create.id

async def update(*, session: AsyncSession, salary_template_update: SalaryTemplate, branch_id: int, id: int) -> SalaryTemplate:
    # 기존 정책 조회
    salary_template = await find_by_id(
        session=session, id=id
    )
    if salary_template is None:
        raise NotFoundError(f"{branch_id}번 지점의 {id}번 연봉 템플릿이 존재하지 않습니다.")
    # 변경된 필드만 업데이트
    changed_fields = {}
    for column in SalaryTemplate.__table__.columns:
        if column.name not in ['id', 'branch_id', 'created_at', 'updated_at', 'deleted_yn']:
            new_value = getattr(salary_template_update, column.name)
            if new_value is not None and getattr(salary_template, column.name) != new_value:
                changed_fields[column.name] = new_value
    if changed_fields:
        # 변경된 필드가 있을 경우에만 업데이트 수행
        stmt = sa_update(SalaryTemplate).where(SalaryTemplate.branch_id == branch_id).where(SalaryTemplate.id == id).values(**changed_fields)
        await session.execute(stmt)
        salary_template.updated_at = datetime.now()
        await session.commit()
        await session.refresh(salary_template)
    else:
        pass
    return salary_template
async def delete(*, session: AsyncSession, branch_id: int, id: int) -> None:
    salary_template = await find_by_id(session=session, id=id)
    if salary_template is None:
        raise NotFoundError(f"{branch_id}번 지점의 {id}번 연봉 템플릿이 존재하지 않습니다.")
    
    salary_template.deleted_yn = "Y"
    salary_template.updated_at = datetime.now()
    await session.commit()
    return