from sqlalchemy.ext.asyncio import AsyncSession

from app.cruds.user_management.work_contract_history_crud import add_work_contract_history, \
    find_work_contract_history_by_id, find_work_contract_histories_by_user_id
from app.models.users.users_work_contract_history_model import WorkContractHistory


class UserManagementWorkContractHistoryService:
    async def create_work_contract_history(
            self,
            session: AsyncSession,
            user_id: int,
            work_contract_id: int,
            change_reason: str = None,
            note: str = None
    ) -> int:
        work_contract_history = WorkContractHistory(
            user_id=user_id,
            work_contract_id=work_contract_id,
            change_reason=change_reason,
            note=note
        )

        created_work_contract_history_id = await add_work_contract_history(
            session=session,
            work_contract_history=work_contract_history
        )

        return created_work_contract_history_id

    async def get_work_contract_history_by_id(
            self,
            work_contract_histories_id: int,
            session: AsyncSession
    ) -> WorkContractHistory:
        return await find_work_contract_history_by_id(
            session=session,
            work_contract_history_id=work_contract_histories_id
       )

    async def get_work_contract_histories_by_user_id(
            self,
            user_id: int,
            session: AsyncSession
    ) -> list[WorkContractHistory]:
        return await find_work_contract_histories_by_user_id(
            session=session,
            user_id=user_id
        )