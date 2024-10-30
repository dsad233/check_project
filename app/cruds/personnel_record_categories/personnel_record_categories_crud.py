import logging
from datetime import datetime
from typing import Optional
from fastapi import HTTPException
from sqlalchemy import func, select, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.branches.personnel_record_categories_model import PersonnelRecordCategory, PersonnelRecordCategoryDto
from app.exceptions.exceptions import NotFoundError

logger = logging.getLogger(__name__)

async def create(
    *, branch_id: int, session: AsyncSession, category_create: PersonnelRecordCategoryDto
) -> int:
    try:
        # 동일한 이름의 카테고리가 있는지 확인
        existing_category = await find_by_name_and_branch_id(
            session=session, 
            branch_id=branch_id, 
            name=category_create.name
        )
        if existing_category:
            raise HTTPException(
                status_code=400, 
                detail=f"{branch_id}번 지점의 인사기록 카테고리 이름 {category_create.name}이(가) 이미 존재합니다."
            )

        # DTO를 SQLAlchemy 모델로 변환
        db_category = PersonnelRecordCategory(
            branch_id=branch_id,
            name=category_create.name,
            description=category_create.description
        )
        
        session.add(db_category)
        await session.commit()
        await session.refresh(db_category)
        return db_category.id
    
    except Exception as error:
        await session.rollback()
        if isinstance(error, HTTPException):
            raise error
        logger.error(f"Error creating personnel record category: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def find_by_name_and_branch_id(
    *, session: AsyncSession, branch_id: int, name: str
) -> Optional[PersonnelRecordCategory]:
    statement = (
        select(PersonnelRecordCategory)
        .where(PersonnelRecordCategory.branch_id == branch_id)
        .where(PersonnelRecordCategory.name == name)
        .where(PersonnelRecordCategory.deleted_yn == "N")
    )
    result = await session.execute(statement)
    return result.scalar_one_or_none()

async def find_all_by_branch_id(
    *, session: AsyncSession, branch_id: int
) -> list[PersonnelRecordCategory]:
    statement = (
        select(PersonnelRecordCategory)
        .where(PersonnelRecordCategory.branch_id == branch_id)
        .where(PersonnelRecordCategory.deleted_yn == "N")
    )
    result = await session.execute(statement)
    return result.scalars().all()

async def find_by_id_and_branch_id(
    *, session: AsyncSession, branch_id: int, category_id: int
) -> PersonnelRecordCategory:
    stmt = (
        select(PersonnelRecordCategory)
        .where(PersonnelRecordCategory.branch_id == branch_id)
        .where(PersonnelRecordCategory.deleted_yn == 'N')
        .where(PersonnelRecordCategory.id == category_id)
    )
    result = await session.execute(stmt)
    category = result.scalar_one_or_none()
    return category

async def count_all(
    *, session: AsyncSession, branch_id: int
) -> int:
    statement = (
        select(func.count(PersonnelRecordCategory.id))
        .where(PersonnelRecordCategory.deleted_yn == "N")
        .where(PersonnelRecordCategory.branch_id == branch_id)
    )
    result = await session.execute(statement)
    return result.scalar_one_or_none()

async def update(
    *, session: AsyncSession, branch_id: int, category_id: int, category_update: PersonnelRecordCategoryDto
) -> None:
    try:
        category = await find_by_id_and_branch_id(
            session=session, 
            branch_id=branch_id, 
            category_id=category_id
        )

        if category is None:
            raise NotFoundError(f"{branch_id}번 지점의 {category_id}번 인사기록 카테고리가 존재하지 않습니다.")

        # 변경된 필드만 업데이트
        update_data = category_update.model_dump(exclude_unset=True)
        
        if 'name' in update_data:
            category.name = update_data['name']
        if 'description' in update_data:
            category.description = update_data['description']

        category.updated_at = datetime.now()
        await session.commit()
        await session.refresh(category)
    
    except Exception as error:
        await session.rollback()
        if isinstance(error, NotFoundError):
            raise
        logger.error(f"Error updating personnel record category: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def delete(
    *, session: AsyncSession, branch_id: int, category_id: int
) -> None:
    category = await find_by_id_and_branch_id(
        session=session, 
        branch_id=branch_id, 
        category_id=category_id
    )
    if category is None:
        raise NotFoundError(f"{branch_id}번 지점의 {category_id}번 인사기록 카테고리를 찾을 수 없습니다.")
    
    category.deleted_yn = "Y"
    category.updated_at = datetime.now()
    await session.commit() 