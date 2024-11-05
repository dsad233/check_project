from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.users.part_timer.users_part_timer_work_contract_model import PartTimerWorkContract, \
    PartTimerWorkingTime, PartTimerHourlyWage
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

    async def partial_update_part_time_contract(self, contract_id: int, update_params: dict):
        # 중첩된 리스트 필드를 분리
        working_times = update_params.pop("working_times", None)
        hourly_wages = update_params.pop("hourly_wages", None)

        # 기본 필드 부분 업데이트 수행
        if update_params:
            stmt = (
                update(PartTimerWorkContract)
                .where(PartTimerWorkContract.id == contract_id)
                .values(**update_params)
            )
            await self.session.execute(stmt)

        # 중첩된 리스트 필드 업데이트
        if working_times is not None:
            await self._update_working_times(contract_id, working_times)
        if hourly_wages is not None:
            await self._update_hourly_wages(contract_id, hourly_wages)

        # 트랜잭션 커밋
        await self.session.commit()

    async def _update_working_times(self, contract_id: int, working_times: list):
        # 기존 `working_times` 데이터를 모두 삭제하고 새 데이터로 대체
        await self.session.execute(
            delete(PartTimerWorkingTime).where(PartTimerWorkingTime.part_timer_work_contract_id == contract_id)
        )
        for time_data in working_times:
            new_working_time = PartTimerWorkingTime(part_timer_work_contract_id=contract_id, **time_data)
            self.session.add(new_working_time)

    async def _update_hourly_wages(self, contract_id: int, hourly_wages: list):
        # 기존 `hourly_wages` 데이터를 모두 삭제하고 새 데이터로 대체
        await self.session.execute(
            delete(PartTimerHourlyWage).where(PartTimerHourlyWage.part_timer_work_contract_id == contract_id)
        )
        for wage_data in hourly_wages:
            new_hourly_wage = PartTimerHourlyWage(part_timer_work_contract_id=contract_id, **wage_data)
            self.session.add(new_hourly_wage)