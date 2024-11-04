from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.users.part_timer.users_part_timer_work_contract_model import PartTimerWorkContract
from app.schemas.user_management.part_timers_contract_schemas import PartTimerWorkContractDto


class UserManagementPartTimeContractRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_dto_by_id(self, part_time_contract_id: int) -> PartTimerWorkContractDto:
        part_time_contract = await self.find_part_time_contract_by_id(part_time_contract_id=part_time_contract_id)
        return PartTimerWorkContractDto.build(part_time_contract=part_time_contract)

    async def find_part_time_contract_by_id(self, part_time_contract_id: int) -> PartTimerWorkContract:
        stmt = (
            select(PartTimerWorkContract)
            .options(
                joinedload(PartTimerWorkContract.part_timer_working_times),
                joinedload(PartTimerWorkContract.part_timer_hourly_wages),
            )
            .filter(
                PartTimerWorkContract.id == part_time_contract_id,
                PartTimerWorkContract.deleted_yn == "N"
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, part_time_contract: PartTimerWorkContract) -> int:
        self.session.add(part_time_contract)
        await self.session.commit()
        await self.session.refresh(part_time_contract)
        return part_time_contract.id