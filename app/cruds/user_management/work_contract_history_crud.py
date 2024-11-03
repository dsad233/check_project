from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.users.users_work_contract_history_model import ContractHistory


class UserManagementContractHistoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def find_work_contract_history_by_id(self, contract_history_id: int) -> ContractHistory:
        stmt = (
            select(ContractHistory)
            .options(selectinload(ContractHistory.user))
            .options(selectinload(ContractHistory.contract_info))
            .filter(
                ContractHistory.id == contract_history_id,
                ContractHistory.deleted_yn == "N"
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def find_contract_histories_by_user_id(self, user_id: int) -> list[ContractHistory]:
        stmt = (
            select(ContractHistory)
            .filter(
                ContractHistory.user_id == user_id,
                ContractHistory.deleted_yn == "N"
            )
            .order_by(ContractHistory.created_at.desc())  # 최신순 정렬
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())  # 모든 결과 반환


    async def add_contract_history(self, contract_history: ContractHistory) -> int:
        self.session.add(contract_history)
        await self.session.commit()
        await self.session.refresh(contract_history)
        return contract_history.id
