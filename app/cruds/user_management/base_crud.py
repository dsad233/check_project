from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.models.branches.branches_model import Branches
from app.models.users.users_model import Users


class UserManagementRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_user_by_user_id(
            self,
            user_id: int
    ) -> Optional[Users]:
        stmt = (
            select(Users)
            .options(joinedload(Users.branch))
            .options(selectinload(Users.part))
            .where(Users.id == user_id)
            .where(Users.deleted_yn == "N")
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()
