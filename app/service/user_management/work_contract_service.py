from app.cruds.user_management.work_contract_crud import UserManagementWorkContractRepository
from app.models.users.users_work_contract_model import WorkContract
from app.schemas.user_work_contract_schemas import WorkContractDto
from app.service.user_management.work_contract_history_service import UserManagementContractHistoryService

class UserManagementWorkContractService:
    def __init__ (
            self,
            work_contract_history_service: UserManagementContractHistoryService,
            work_contract_repository: UserManagementWorkContractRepository,
    ):
        self.work_contract_history_service = work_contract_history_service
        self.work_contract_repository = work_contract_repository

    async def get_work_contract_by_id(self, work_contract_id: int) -> WorkContractDto:
        return await self.work_contract_repository.find_dto_by_work_contract_id(
            work_contract_id=work_contract_id
        )

    async def create_work_contract(
            self,
            work_contract: WorkContract,
    ):
        created_work_contract_id = await self.work_contract_repository.add_work_contract(work_contract=work_contract)
        return created_work_contract_id


    async def partial_update_work_contract(
            self,
            work_contract_id: int,
            update_params: dict,
    ) -> WorkContractDto:
        updated_work_contract = await self.work_contract_repository.partial_update_work_contract(
            contract_id=work_contract_id,
            update_params=update_params,
        )
        return updated_work_contract