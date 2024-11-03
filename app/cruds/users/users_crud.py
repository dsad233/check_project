from datetime import datetime
import logging
from typing import Optional
from fastapi import Depends
from sqlalchemy import func, select, update as sa_update, distinct
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from app.models.users.users_model import Users, PersonnelRecordHistory
from app.models.branches.branches_model import Branches
from app.models.branches.work_policies_model import WorkPolicies
from app.models.parts.parts_model import Parts
from app.schemas.users_schemas import PersonnelRecordUsersRequest
from app.common.dto.search_dto import BaseSearchDto, NamePhoneSearchDto
from app.exceptions.exceptions import BadRequestError


logger = logging.getLogger(__name__)

async def find_by_id(
    *, session: AsyncSession, user_id: int
) -> Optional[Users]:

    stmt = select(Users).where(Users.id == user_id).where(Users.deleted_yn == "N")
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return user

async def find_by_email(
    *, session: AsyncSession, email: str
) -> Optional[Users]:
    
    stmt = select(Users).where(Users.email == email).where(Users.deleted_yn == "N")
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def find_all_by_branch_id_and_role(
    *, session: AsyncSession, branch_id: int, role: str
) -> Optional[list[Users]]:
    stmt = select(Users).where(Users.branch_id == branch_id).where(Users.role == role).where(Users.deleted_yn == "N")
    result = await session.execute(stmt)
    users = list(result.scalars().all())
    return users

async def add_user(
        *, session: AsyncSession, user: Users
) -> Users:
    try:
        user.created_at = datetime.now()
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
    except SQLAlchemyError as e:
        logger.error(f"Failed to add user: {e}")
        await session.rollback()
        raise e

async def update_user(
        *, session: AsyncSession, old: Users, request: dict
) -> Users:
    for key, value in request.items():
        setattr(old, key, value)
    old.updated_at = datetime.now()
    
    session.flush()
    session.refresh(old)

    return old
    

async def update_total_leave_days(
    *, session: AsyncSession, user_id: int, count: int
) -> bool:
    await session.execute(
        sa_update(Users)
        .where(Users.id == user_id)
        .values(
            total_leave_days=count,
            updated_at=datetime.now()
        )
    )
    await session.flush()
    return True


async def get_users_count(
    *, session: AsyncSession, branch_id: int
) -> int:
    stmt = select(func.count()).where(Users.branch_id == branch_id).where(Users.deleted_yn == "N")
    result = await session.execute(stmt)
    return result.scalar_one()


async def create_personnel_record_history(
    *, session: AsyncSession, request: PersonnelRecordHistory
) -> PersonnelRecordHistory:
    session.add(request)
    await session.flush()

    return request


async def get_personnel_record_histories(
    *, session: AsyncSession, user_id: int, request: BaseSearchDto
) -> list[PersonnelRecordHistory]:
    stmt = (
        select(PersonnelRecordHistory)
        .options(
            joinedload(PersonnelRecordHistory.user),
            joinedload(PersonnelRecordHistory.created_by_user),
            joinedload(PersonnelRecordHistory.personnel_record_category),
        )
        .where(PersonnelRecordHistory.deleted_yn == "N")
        .where(PersonnelRecordHistory.user_id == user_id)
    )

    stmt = stmt.offset(request.offset).limit(request.record_size)
    result = await session.execute(stmt)
    return result.unique().scalars().all()


async def get_personnel_record_histories_count(
    *, session: AsyncSession, user_id: int
) -> int:
    stmt = select(func.count()).where(PersonnelRecordHistory.user_id == user_id).where(PersonnelRecordHistory.deleted_yn == "N")
    result = await session.execute(stmt)
    return result.scalar_one()


async def get_personnel_record_history(
    *, session: AsyncSession, id: int
) -> PersonnelRecordHistory:
    stmt = (
        select(PersonnelRecordHistory)
        .options(
            joinedload(PersonnelRecordHistory.user),
            joinedload(PersonnelRecordHistory.created_by_user),
            joinedload(PersonnelRecordHistory.personnel_record_category),
        )
        .where(PersonnelRecordHistory.id == id)
        .where(PersonnelRecordHistory.deleted_yn == "N")
    )
    result = await session.execute(stmt)
    return result.scalar_one()


async def update_personnel_record_history(
    *, session: AsyncSession, old: PersonnelRecordHistory, request: dict
) -> bool:
    for key, value in request.items():
        setattr(old, key, value)
    old.updated_at = datetime.now()
    session.flush()

    return True

async def delete_personnel_record_history(
    *, session: AsyncSession, id: int
) -> bool:
    await session.execute(
        sa_update(PersonnelRecordHistory).where(PersonnelRecordHistory.id == id).values(deleted_yn="Y")
    )
    await session.flush()
    return True


async def get_personnel_record_users(
    *, session: AsyncSession, request: PersonnelRecordUsersRequest
) -> tuple[list[Users], int]:
    
    base_query = (
        select(Users)
        .join(Users.branch)
        .join(Users.part)
        .options(
            joinedload(Users.part),
            joinedload(Users.branch).joinedload(
                Branches.work_policies.and_(WorkPolicies.deleted_yn == "N")
            ),
            selectinload(Users.personnel_record_histories)
        )
        .where(
            Users.deleted_yn == "N",
            Branches.deleted_yn == "N",
            Parts.deleted_yn == "N"
        )
    )

    if request.name:
        base_query = base_query.where(Users.name.ilike(f"%{request.name}%"))
    if request.phone_number:
        base_query = base_query.where(Users.phone_number.ilike(f"%{request.phone_number}%"))
    if request.branch_id:
        base_query = base_query.where(Users.branch_id == request.branch_id)
    if request.part_id:
        base_query = base_query.where(Users.part_id == request.part_id)

    # 전체 카운트
    count_query = select(func.count()).select_from(base_query.subquery())
    total_count = await session.scalar(count_query)

    # 결과 조회
    result = await session.execute(
        base_query
        .order_by(Users.created_at.desc())
        .offset(request.offset)
        .limit(request.record_size)
    )

    return result.unique().scalars().all(), total_count


async def get_branch_users(
    *, session: AsyncSession, request: BaseSearchDto, branch_id: int
) -> tuple[list[Users], int]:
    base_query = (
        select(Users)
        .join(Users.part)
        .options(
            joinedload(Users.part),
        )
        .where(
            Users.deleted_yn == "N",
            Parts.deleted_yn == "N",
            Users.branch_id == branch_id
        )
    )

    count_query = select(func.count()).select_from(base_query.subquery())
    total_count = await session.scalar(count_query)

    result = await session.execute(
        base_query
        .order_by(Users.created_at.desc())
        .offset(request.offset)
        .limit(request.record_size)
    )

    return result.unique().scalars().all(), total_count