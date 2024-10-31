from typing import Optional
from sqlalchemy import func, select, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.parts.parts_model import Parts
from datetime import datetime


async def find_by_id(
    *, session: AsyncSession, part_id: int
) -> Optional[Parts]:
    stmt = (
        select(Parts)
        .where(Parts.deleted_yn == 'N')
        .where(Parts.id == part_id)
    )
    result = await session.execute(stmt)
    part = result.scalar_one_or_none()
    
    return part


async def find_by_name_and_branch_id(
    *, session: AsyncSession, name: str, branch_id: int
) -> Optional[Parts]:
    stmt = select(Parts).where(Parts.name == name).where(Parts.branch_id == branch_id).where(Parts.deleted_yn == 'N')
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def find_all_by_branch_id(
    *, session: AsyncSession, branch_id: int
) -> list[Parts]:
    stmt = (
        select(Parts).where(Parts.branch_id == branch_id).where(Parts.deleted_yn == 'N')
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def update_auto_annual_leave_grant(
    *, session: AsyncSession, part_id: int, request: str, old: Parts
) -> bool:

    if old.auto_annual_leave_grant != request:
        await session.execute(
            sa_update(Parts)
            .where(Parts.id == part_id)
            .values(auto_annual_leave_grant=request)
        )

        await session.commit()
        await session.refresh(old)
    else:
        pass

    return True
    

async def find_all_by_auto_annual_leave_grant(
    *, session: AsyncSession, request: str
) -> list[Parts]:
    stmt = (
        select(Parts)
        .where(Parts.auto_annual_leave_grant == request)
        .where(Parts.deleted_yn == 'N')
    )
    result = await session.execute(stmt)
    return result.scalars().all()
    

async def delete_part(
    *, session: AsyncSession, part_id: int
) -> bool:
    await session.execute(sa_update(Parts).where(Parts.id == part_id).values(deleted_yn='Y'))
    await session.commit()
    return True


async def update_part(
    *, session: AsyncSession, part_id: int, request: Parts, old: Parts
) -> bool:
    # 변경된 필드만 업데이트
    changed_fields = {}
    for column in Parts.__table__.columns:
        if column.name not in ['id', 'created_at', 'updated_at', 'deleted_yn']:
            new_value = getattr(request, column.name)
            if new_value is not None and getattr(old, column.name) != new_value:
                changed_fields[column.name] = new_value

    if changed_fields:
        # 변경된 필드가 있을 경우에만 업데이트 수행
        stmt = sa_update(Parts).where(Parts.id == part_id).values(**changed_fields)
        await session.execute(stmt)
        old.updated_at = datetime.now()
        await session.commit()
        await session.refresh(old)
    else:
        pass
    
    return True


async def create_part(
    *, session: AsyncSession, request: Parts
) -> Parts:
    
    session.add(request)
    await session.commit()
    await session.flush()
    await session.refresh(request)

    return request