from app.cruds.user_management.work_contract_history_crud import UserManagementContractHistoryRepository
from app.models.users.users_work_contract_history_model import ContractHistory


class UserManagementContractHistoryService:
    def __init__(self, contract_history_repository: UserManagementContractHistoryRepository):
        self.contract_history_repository = contract_history_repository

    async def get_contract_history_by_id(self, contract_history_id: int) -> ContractHistory:
        return await self.contract_history_repository.find_work_contract_history_by_id(contract_history_id=contract_history_id)

    async def get_contract_histories_by_user_id(self, user_id: int) -> list[ContractHistory]:
        return await self.contract_history_repository.find_contract_histories_by_user_id(user_id=user_id)

    async def create_contract_history(self, contract_history: ContractHistory) -> int:
        return await self.contract_history_repository.add_contract_history(contract_history=contract_history)
