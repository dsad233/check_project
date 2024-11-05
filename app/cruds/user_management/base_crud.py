from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.enums.users import Role
from app.models.branches.branches_model import Branches
from app.models.users.users_contract_info_model import ContractInfo
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
            .options(
                joinedload(Users.contract_info).joinedload(ContractInfo.part),
                joinedload(Users.branch),
                joinedload(Users.part)
            )
            .where(Users.id == user_id)
            .where(Users.deleted_yn == "N")
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def update_user_role(self, user_id: int, role: Role) -> bool:
        stmt = (
            update(Users)
            .where(Users.id == user_id)
            .values(role=role)
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return True

