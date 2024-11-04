from app.cruds.user_management.part_time_contract_crud import UserManagementPartTimeContractRepository
from app.models.users.part_timer.users_part_timer_work_contract_model import PartTimerWorkContract
from app.schemas.user_management.part_timers_contract_schemas import PartTimerWorkContractDto


class UserManagementPartTimeContractService:
    def __init__(self, part_time_contract_repository: UserManagementPartTimeContractRepository):
        self.part_time_contract_repository = part_time_contract_repository

    async def create_part_time_contract(self, part_time_contract: PartTimerWorkContract) -> int:
        return await self.part_time_contract_repository.create(part_time_contract=part_time_contract)

    async def get_part_time_contract_by_id(self, part_time_contract_id: int) -> PartTimerWorkContractDto:
        return await self.part_time_contract_repository.find_dto_by_id(part_time_contract_id=part_time_contract_id)