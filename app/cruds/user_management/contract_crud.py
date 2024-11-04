import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select, insert, text, update
from sqlalchemy.orm import selectinload, joinedload

from app.models.users.users_contract_model import Contract, ContractSendMailHistory
from app.models.users.users_model import Users

logger = logging.getLogger(__name__)

class UserManagementContractRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_user_by_id_with_contracts(self, user_id: int) -> Optional[Users]:
        stmt = (
            select(Users)
            # user_id 관계로 연결된 contracts 로드
            .options(selectinload(Users.contracts_user_id)
            # 각 contract의 manager 정보도 로드
            .options(joinedload(Contract.manager)),
                # manager_id 관계로 연결된 contracts 로드
                selectinload(Users.contracts_manager_id)
            )
            .where(Users.id == user_id)
            .where(Users.deleted_yn == "N")
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def find_contract_by_contract_id(self, contract_id: int) -> Optional[Contract]:
        stmt = (
            select(Contract)
            .filter(
                Contract.id == contract_id,
                Contract.deleted_yn == "N"
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def find_contract_by_modusign_id(self, modusign_id: str) -> Optional[Contract]:
        stmt = (
            select(Contract)
            .options(joinedload(Contract.user))
            .options(joinedload(Contract.manager))
            .options(joinedload(Contract.work_contract))
            # .options(joinedload(Contract.work_contract_histories))
            .where(
                Contract.modusign_id == modusign_id,
                Contract.deleted_yn == "N"
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def find_contract_send_mail_histories_by_user_id(self, user_id: int) -> list[ContractSendMailHistory]:
        stmt = (
            select(ContractSendMailHistory)
            .options(joinedload(ContractSendMailHistory.request_user))
            .options(joinedload(ContractSendMailHistory.contract))
            .where(ContractSendMailHistory.user_id == user_id)
            .order_by(ContractSendMailHistory.created_at.desc())  # 최신순 정렬
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())  # 모든 결과 반환


    async def add_contracts(self, contracts: list[dict]) -> list[int]:
        try:
            stmt = insert(Contract).values(contracts)
            await self.session.execute(stmt)

            last_id_result = await self.session.execute(text("SELECT LAST_INSERT_ID()"))
            first_id = last_id_result.scalar()

            created_ids = list(range(first_id, first_id + len(contracts)))

            await self.session.commit()
            return created_ids

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to add contracts: {str(e)}")
            raise e

    async def add_contract(self, contract: Contract) -> int:
        try:
            self.session.add(contract)
            await self.session.commit()
            await self.session.refresh(contract)
            return contract.id
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to add contract: {str(e)}")
            raise e

    async def add_contract_send_mail_history(self, contract_send_mail_history_dict: dict):
        try:
            stmt = insert(ContractSendMailHistory).values(contract_send_mail_history_dict)
            await self.session.execute(stmt)
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to add contract send mail history: {str(e)}")
            raise e

    async def soft_delete_contract(self, user_id: int, contract_id: int):
        try:
            stmt = (
                select(Contract)
                .where(Contract.user_id == user_id)
                .where(Contract.id == contract_id)
                .where(Contract.deleted_yn == "N")
            )
            result = await self.session.execute(stmt)
            contract = result.scalar_one_or_none()
            if not contract:
                raise Exception("Contract not found")

            contract.deleted_yn = "Y"
            await self.session.commit()
        except Exception as e:
            logger.error(f"Failed to soft delete contract: {e}")
            await self.session.rollback()
            raise e

    async def hard_delete_contract(self, user_id: int, contract_id: int):
        try:
            stmt = (
                select(Contract)
                .where(Contract.user_id == user_id)
                .where(Contract.id == contract_id)
                .where(Contract.deleted_yn == "Y")
            )
            result = await self.session.execute(stmt)
            contract = result.scalar_one_or_none()
            if not contract:
                raise Exception("Contract not found")

            await self.session.delete(contract)
            await self.session.commit()
        except Exception as e:
            logger.error(f"Failed to hard delete contract: {e}")
            await self.session.rollback()
            raise e

    async def update_contract(self, contract_id: int, update_params: dict):
        try:
            stmt = (
                update(Contract)
                .where(Contract.id == contract_id)
                .values(update_params)
            )
            await self.session.execute(stmt)
            await self.session.commit()
        except Exception as e:
            logger.error(f"Failed to update contract: {e}")
            await self.session.rollback()
            raise e