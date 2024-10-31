from datetime import datetime
from typing import Optional
from sqlalchemy import select, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.parts.hour_wage_template_model import HourWageTemplate


async def create(
    *, branch_id: int, session: AsyncSession, request: HourWageTemplate
) -> HourWageTemplate:
    
    session.add(request)
    await session.commit()
    await session.refresh(request)
    return request

async def find_by_name_and_branch_id(
    *, session: AsyncSession, branch_id: int, name: str
) -> Optional[HourWageTemplate]:
    
    stmt = select(HourWageTemplate).where(HourWageTemplate.branch_id == branch_id).where(HourWageTemplate.name == name).where(HourWageTemplate.deleted_yn == "N")
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
    

async def find_by_id(
    *, branch_id: int, hour_wage_template_id: int, session: AsyncSession
) -> Optional[HourWageTemplate]:
        
    stmt = select(HourWageTemplate).where(HourWageTemplate.branch_id == branch_id).where(HourWageTemplate.id == hour_wage_template_id).where(HourWageTemplate.deleted_yn == 'N')
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def find_all_by_branch_id(
    *, branch_id: int, session: AsyncSession
) -> list[HourWageTemplate]:
    
    stmt = select(HourWageTemplate).where(HourWageTemplate.branch_id == branch_id).where(HourWageTemplate.deleted_yn == "N")
    result = await session.execute(stmt)
    return result.scalars().all()

async def update(
    *, branch_id: int, hour_wage_template_id: int, session: AsyncSession, request: HourWageTemplate, old: HourWageTemplate
) -> bool:

    # 변경된 필드만 업데이트
    changed_fields = {}
    for column in HourWageTemplate.__table__.columns:
        if column.name not in ['id', 'branch_id', 'created_at', 'updated_at', 'deleted_yn']:
            new_value = getattr(request, column.name)
            if column.name == 'part_id' and new_value is None:
                changed_fields[column.name] = None
            if new_value is not None and getattr(old, column.name) != new_value:
                changed_fields[column.name] = new_value

    if changed_fields:
        # 변경된 필드가 있을 경우에만 업데이트 수행
        stmt = sa_update(HourWageTemplate).where(HourWageTemplate.branch_id == branch_id).where(HourWageTemplate.id == hour_wage_template_id).values(**changed_fields)
        await session.execute(stmt)
        old.updated_at = datetime.now()
        await session.commit()
        await session.refresh(old)
    else:
        pass

    return True

async def delete(
    *, branch_id: int, hour_wage_template_id: int, session: AsyncSession
) -> bool:
        
    await session.execute(
            sa_update(HourWageTemplate)
            .where(HourWageTemplate.id == hour_wage_template_id)
            .values(
                deleted_yn="Y",
                updated_at=datetime.now()
            )
        )
    await session.commit()
    return True