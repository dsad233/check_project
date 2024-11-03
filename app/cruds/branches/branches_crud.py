import logging
from datetime import datetime
from sqlalchemy import func, select, update as sa_update, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from sqlalchemy.orm import selectinload, joinedload
from app.models.branches.branches_model import Branches, PersonnelRecordCategory
from app.common.dto.search_dto import BaseSearchDto
from app.models.branches.work_policies_model import WorkPolicies
from app.models.parts.parts_model import Parts
from app.models.users.users_model import Users

logger = logging.getLogger(__name__)


async def find_by_name(
    *, session: AsyncSession, name: str
) -> Optional[Branches]:
    stmt = select(Branches).where(Branches.name == name).where(Branches.deleted_yn == 'N')
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create(
    *, session: AsyncSession, request: Branches
) -> Branches:

    session.add(request)
    await session.commit()
    await session.flush()
    await session.refresh(request)
    return request


async def find_all_by_limit(
    *, session: AsyncSession, request: BaseSearchDto
) -> list[Branches]:

    statement = (
        select(Branches).filter(Branches.deleted_yn == "N").offset(request.offset).limit(request.record_size)
    )
    result = await session.execute(statement)
    return result.scalars().all()

async def find_all(
    *, session: AsyncSession
) -> list[Branches]:

    statement = (
        select(Branches).where(Branches.deleted_yn == "N")
    )
    result = await session.execute(statement)
    return result.scalars().all()


async def find_deleted_all(
    *, session: AsyncSession, request: BaseSearchDto
) -> list[Branches]:

    statement = (
        select(Branches).filter(Branches.deleted_yn == "Y").offset(request.offset).limit(request.record_size)
    )
    result = await session.execute(statement)
    return result.scalars().all()


async def count_all(*, session: AsyncSession) -> int:

    statement = select(func.count()).select_from(Branches)
    result = await session.execute(statement)
    return result.scalar_one()


async def find_by_id(
    *, session: AsyncSession, branch_id: int
) -> Optional[Branches]:
    
    statement = select(Branches).filter(Branches.id == branch_id).where(Branches.deleted_yn == 'N')
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def find_by_id_with_policies(
    *, session: AsyncSession, branch_id: int
) -> Optional[Branches]:
    stmt = select(Branches).options(
        joinedload(Branches.work_policies).options(
            selectinload(WorkPolicies.work_schedules),
            selectinload(WorkPolicies.break_times),
        ),
        joinedload(Branches.overtime_policies),
        joinedload(Branches.holiday_work_policies),
        joinedload(Branches.auto_overtime_policies),
        joinedload(Branches.account_based_annual_leave_grant),
        joinedload(Branches.entry_date_based_annual_leave_grant),
        joinedload(Branches.condition_based_annual_leave_grant),
        joinedload(Branches.auto_annual_leave_approval),
        joinedload(Branches.allowance_policies)
    ).where(Branches.id == branch_id).where(Branches.deleted_yn == "N")
    
    result = await session.execute(stmt)
    branch = result.scalar_one_or_none()
    return branch


async def delete(*, session: AsyncSession, branch_id: int) -> bool:

    await session.execute(
            sa_update(Branches)
            .where(Branches.id == branch_id)
            .values(
                deleted_yn="Y",
                updated_at=datetime.now()
            )
        )
    await session.commit()
    return True

async def revive(*, session: AsyncSession, branch_id: int) -> bool:

    await session.execute(
            sa_update(Branches)
            .where(Branches.id == branch_id)
            .values(
                deleted_yn="N",
                updated_at=datetime.now()
            )
        )
    await session.commit()
    return True

async def count_deleted_all(*, session: AsyncSession) -> int:

    statement = select(func.count()).select_from(Branches).where(Branches.deleted_yn == "Y")
    result = await session.execute(statement)
    return result.scalar_one()

async def update(*, session: AsyncSession, branch_id: int, request: Branches, old: Branches) -> bool:
    # 변경된 필드만 업데이트
    changed_fields = {}
    for column in Branches.__table__.columns:
        if column.name not in ['id', 'created_at', 'updated_at', 'deleted_yn']:
            new_value = getattr(request, column.name)
            if new_value is not None and getattr(old, column.name) != new_value:
                changed_fields[column.name] = new_value

    if changed_fields:
        # 변경된 필드가 있을 경우에만 업데이트 수행
        stmt = sa_update(Branches).where(Branches.id == branch_id).values(**changed_fields)
        await session.execute(stmt)
        old.updated_at = datetime.now()
        await session.commit()
        await session.refresh(old)
    else:
        pass
    
    return True


# async def find_all_with_parts_users_auto_annual_leave_policies(
#     *, session: AsyncSession
# ) -> list[Branches]:
#     stmt = select(Branches).options(
#         selectinload(Branches.parts.and_(Parts.deleted_yn == "N")
#                      ).selectinload(Parts.users.and_(Users.deleted_yn == "N")),
#         selectinload(Branches.account_based_annual_leave_grant),
#         selectinload(Branches.entry_date_based_annual_leave_grant),
#         selectinload(Branches.condition_based_annual_leave_grant)
#         ).where(Branches.deleted_yn == "N")
#     result = await session.execute(stmt)
#     return result.scalars().all()


async def find_all_with_parts_users_auto_annual_leave_policies(
    *, session: AsyncSession
) -> list[Branches]:
    stmt = (
       select(Branches)
       .options(
           selectinload(
               Branches.parts.and_(Parts.deleted_yn == "N")
            ).selectinload(
               Parts.users.and_(Users.deleted_yn == "N")
           ),
           joinedload(Branches.account_based_annual_leave_grant),
           joinedload(Branches.entry_date_based_annual_leave_grant),
           joinedload(Branches.condition_based_annual_leave_grant)
       )
       .where(Branches.deleted_yn == "N")
   )
    result = await session.execute(stmt)
    return result.unique().scalars().all()


async def create_personnel_record_category(
    *, session: AsyncSession, request: PersonnelRecordCategory
) -> PersonnelRecordCategory:
    session.add(request)
    await session.flush()

    return request


async def get_personnel_record_categories_total_cnt(
    *, session: AsyncSession, branch_id: int
) -> int:
    stmt = select(func.count()).select_from(PersonnelRecordCategory).where(PersonnelRecordCategory.branch_id == branch_id).where(PersonnelRecordCategory.deleted_yn == "N")
    result = await session.execute(stmt)

    return result.scalar_one()


async def get_personnel_record_categories(
    *, session: AsyncSession, branch_id: int, request: BaseSearchDto
) -> list[PersonnelRecordCategory]:
    stmt = (
        select(PersonnelRecordCategory)
        .where(PersonnelRecordCategory.branch_id == branch_id)
        .where(PersonnelRecordCategory.deleted_yn == "N")
        .offset(request.offset)
        .limit(request.record_size)
    )
    result = await session.execute(stmt)

    return result.scalars().all()


async def get_personnel_record_category(
    *, session: AsyncSession, id: int
) -> PersonnelRecordCategory:
    stmt = select(PersonnelRecordCategory).where(PersonnelRecordCategory.id == id).where(PersonnelRecordCategory.deleted_yn == "N")
    result = await session.execute(stmt)

    return result.scalar_one_or_none()


async def get_personnel_record_category_by_name(
    *, session: AsyncSession, name: str, branch_id: int
) -> PersonnelRecordCategory:
    stmt = select(PersonnelRecordCategory).where(PersonnelRecordCategory.name == name).where(PersonnelRecordCategory.branch_id == branch_id).where(PersonnelRecordCategory.deleted_yn == "N")
    result = await session.execute(stmt)

    return result.scalar_one_or_none()


async def update_personnel_record_category(
    *, session: AsyncSession, old: PersonnelRecordCategory, request: dict
) -> PersonnelRecordCategory:
    for key, value in request.items():
        setattr(old, key, value)
    old.updated_at = datetime.now()
    
    session.flush()
    session.refresh(old)

    return old


async def delete_personnel_record_category(
    *, session: AsyncSession, id: int
) -> bool:
    await session.execute(sa_update(PersonnelRecordCategory).where(PersonnelRecordCategory.id == id).values(deleted_yn="Y"))
    await session.flush()

    return True
