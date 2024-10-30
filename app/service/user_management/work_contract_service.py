from sqlalchemy.ext.asyncio import AsyncSession

from app.cruds.user_management.work_contract_crud import add_work_contract
from app.models.users.users_work_contract_model import WorkContract




class UserManagementWorkContractService:
    async def create_work_contract(
            self,
            session: AsyncSession,
            work_contract: WorkContract
    ):
        created_work_contract_id = await add_work_contract(session=session, work_contract=work_contract)
        # work contract history 추가

        return created_work_contract_id

