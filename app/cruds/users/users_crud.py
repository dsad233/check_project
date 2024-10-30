from datetime import datetime
import logging
from typing import Optional
from fastapi import Depends
from sqlalchemy import func, select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from app.models.users.users_model import Users
from app.common.dto.search_dto import BaseSearchDto
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

async def find_all_by_branch_id(
    *, session: AsyncSession, branch_id: int, request: BaseSearchDto
) -> list[Users]:
    stmt = select(Users).options(selectinload(Users.part)).where(Users.branch_id == branch_id).where(Users.deleted_yn == "N").offset(request.offset).limit(request.record_size)
    result = await session.execute(stmt)
    users = result.scalars().all()
    return users


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

async def plus_remaining_annual_leave(
    *, session: AsyncSession, user: Users, count: int
) -> Users:
    user.remaining_annual_leave += count
    await session.flush()
    await session.commit()
    await session.refresh(user)
    findUser = await find_by_id(session=session, user_id=user.id)
    print(findUser.remaining_annual_leave)
    return user

async def minus_remaining_annual_leave(
    *, session: AsyncSession, user: Users, count: int
) -> Users:
    if user.remaining_annual_leave < count:
        raise BadRequestError(detail="잔여 연차가 부족합니다.")
    user.remaining_annual_leave -= count
    await session.flush()
    await session.commit()
    await session.refresh(user)
    return user


async def get_users_count(
    *, session: AsyncSession, branch_id: int
) -> int:
    stmt = select(func.count()).where(Users.branch_id == branch_id).where(Users.deleted_yn == "N")
    result = await session.execute(stmt)
    return result.scalar_one()