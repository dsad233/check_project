from sqlalchemy.ext.asyncio import AsyncSession

from app.cruds.user_management.work_contract_crud import add_work_contract
from app.models.users.users_work_contract_history_model import WorkContractHistory
from app.models.users.users_work_contract_model import WorkContract
from app.service.user_management.work_contract_history_service import UserManagementWorkContractHistoryService

user_management_work_contract_history_service = UserManagementWorkContractHistoryService()

class UserManagementWorkContractService:
    async def create_work_contract(
            self,
            session: AsyncSession,
            work_contract: WorkContract,
            change_reason: str = None,
            note: str = None
    ):
        created_work_contract_id = await add_work_contract(session=session, work_contract=work_contract)
        await user_management_work_contract_history_service.create_work_contract_history(
            session=session,
            user_id=work_contract.user_id,
            work_contract_id=created_work_contract_id,
            change_reason=change_reason,
            note=note
        )

        return created_work_contract_id


