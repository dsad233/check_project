from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.enums.common import YesNo
from app.models.users.users_contract_info_model import ContractInfo
from app.schemas.user_management.contract_info import ContractInfoDto


class UserManagementContractInfoRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, contract_info_id: int) -> ContractInfo:
        stmt = (
            select(ContractInfo)
            .options(
                joinedload(ContractInfo.part),
                selectinload(ContractInfo.contracts)
            )
            .filter(
                ContractInfo.id == contract_info_id,
                ContractInfo.deleted_yn == "N"
            )
        )

        result = await self.session.execute(stmt)
        return result.scalars().one()

    async def find_activated_contract_infos_by_user_id(self, user_id: int) -> List[ContractInfo]:
        stmt = (
            select(ContractInfo)
            .filter(
                ContractInfo.user_id == user_id,
                ContractInfo.deleted_yn == "N",
                ContractInfo.activate_yn == YesNo.YES
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_dto_by_id(self, contract_info_id: int) -> ContractInfoDto:
        contract_info = await self.find_by_id(contract_info_id=contract_info_id)
        return ContractInfoDto.build(contract_info=contract_info)

    async def create(self, contract_info: ContractInfo) -> int:
        self.session.add(contract_info)
        await self.session.commit()
        return contract_info.id

    async def bulk_update(self, updated_contract_infos: List[ContractInfo]) -> None:
        for updated_contract_info in updated_contract_infos:
            self.session.add(updated_contract_info)
        await self.session.commit()