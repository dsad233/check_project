import logging
from datetime import datetime
from typing import Optional
from fastapi import Depends
from sqlalchemy import func, select, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, NoResultFound

from app.common.dto.search_dto import BaseSearchDto
from app.models.branches.leave_categories_model import LeaveCategory
from app.exceptions.exceptions import BadRequestError, NotFoundError

from fastapi import HTTPException

logger = logging.getLogger(__name__)

async def create(
    *, branch_id: int, session: AsyncSession, leave_category_create: LeaveCategory
) -> int:
    try:
    
        leave_category = await find_by_name_and_branch_id(session=session, branch_id=branch_id, name=leave_category_create.name)
        if leave_category:
            raise HTTPException(status_code=400, detail=f"{branch_id}번 지점의 휴가 카테고리 이름 {leave_category_create.name}이(가) 이미 존재합니다.")

        session.add(leave_category_create)
        await session.commit()
        await session.refresh(leave_category_create)
        return leave_category_create.id
    
    except Exception as error:
        if isinstance(error, HTTPException):
            raise error

        print(error)
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def find_by_name_and_branch_id(
    *, session: AsyncSession, branch_id: int, name: str
) -> Optional[LeaveCategory]:

    statement = (
        select(LeaveCategory)
        .where(LeaveCategory.branch_id == branch_id)
        .where(LeaveCategory.name == name)
        .where(LeaveCategory.deleted_yn == "N")
    )
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def find_all_by_branch_id(
    *, session: AsyncSession, branch_id: int
) -> list[LeaveCategory]:

    statement = (
        select(LeaveCategory)
        .where(LeaveCategory.branch_id == branch_id)
        .where(LeaveCategory.deleted_yn == "N")
    )
    result = await session.execute(statement)
    return result.scalars().all()

async def find_by_id_and_branch_id(
    *, session: AsyncSession, branch_id: int, leave_id: int
) -> LeaveCategory:
    
    stmt = (
        select(LeaveCategory)
        .where(LeaveCategory.branch_id == branch_id)
        .where(LeaveCategory.deleted_yn == 'N')
        .where(LeaveCategory.id == leave_id)
    )
    result = await session.execute(stmt)
    policy = result.scalar_one_or_none()
    
    return policy


async def count_all(*, session: AsyncSession, branch_id: int) -> int:
    
    statement = (
        select(func.count(LeaveCategory.id))
        .where(LeaveCategory.deleted_yn == "N")
        .where(LeaveCategory.branch_id == branch_id)
    )
    result = await session.execute(statement)
    return result.scalar_one_or_none()

async def update(
    *, session: AsyncSession, branch_id: int, leave_category_id: int, leave_category_update: LeaveCategory
) -> None:
        
    # 기존 정책 조회
    leave_category = await find_by_id_and_branch_id(
        session=session, branch_id=branch_id, leave_id=leave_category_id
    )

    if leave_category is None:
        raise NotFoundError(f"{branch_id}번 지점의 {leave_category_id}번 휴가 카테고리가 존재하지 않습니다.")

    # 변경된 필드만 업데이트
    changed_fields = {}
    for column in LeaveCategory.__table__.columns:
        if column.name not in ['id', 'branch_id', 'created_at', 'updated_at', 'deleted_yn']:
            new_value = getattr(leave_category_update, column.name)
            if new_value is not None and getattr(leave_category, column.name) != new_value:
                changed_fields[column.name] = new_value

    if changed_fields:
        # 변경된 필드가 있을 경우에만 업데이트 수행
        stmt = sa_update(LeaveCategory).where(LeaveCategory.branch_id == branch_id).where(LeaveCategory.id == leave_category_id).values(**changed_fields)
        await session.execute(stmt)
        leave_category.updated_at = datetime.now()
        await session.commit()
        await session.refresh(leave_category)
    else:
        pass

    return 


async def delete(
    *, session: AsyncSession, branch_id: int, leave_category_id: int
) -> None:
    
    leave_category = await find_by_id_and_branch_id(
        session=session, branch_id=branch_id, leave_id=leave_category_id
    )
    if leave_category is None:
        raise NotFoundError(f"{branch_id}번 지점의 {leave_category_id}번 휴가 카테고리를 찾을 수 없습니다.")
    leave_category.deleted_yn = "Y"
    leave_category.updated_at = datetime.now()
    await session.commit()
