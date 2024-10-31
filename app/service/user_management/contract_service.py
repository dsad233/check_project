from sqlalchemy.ext.asyncio import AsyncSession

from app.cruds.user_management.contract_crud import add_contract, find_contract_by_contract_id, \
    find_contract_by_modusign_id
from app.enums.users import Role
from app.models.users.users_contract_model import Contract
from app.models.users.users_model import Users
from app.service.template_service import TemplateService as ModusignTemplateService
from app.service.document_service import DocumentService as ModusignDocumentService
from app.service.user_management.service import UserManagementService
from app.service.user_management.work_contract_history_service import UserManagementWorkContractHistoryService
from app.utils.modusign_utils import ModuSignGenerator

modusign_template_service = ModusignTemplateService()
modusign_document_service = ModusignDocumentService()
user_management_service = UserManagementService()
user_management_work_contract_history_service = UserManagementWorkContractHistoryService()

SAMPLE_TEMPLATE_ID = "e7193300-96da-11ef-8b54-adaae74d0aa0"


class UserManagementContractService:
    async def create_contract(
            self,
            user_id: int,
            manager_id: int,
            work_contract_history_id: int,
            session: AsyncSession,
    ) -> int:
        user = await user_management_service.get_user(user_id=user_id, session=session)
        modusign_result = await self.request_contract_by_modusign(user=user)

        modusign_id = modusign_result.get("id")
        contract_name = modusign_result.get("title")
        contract_url = modusign_result.get("file").get("downloadUrl")

        work_contract_history = user_management_work_contract_history_service.get_work_contract_history_by_id(
            work_contract_histories_id=work_contract_history_id,
            session=session
        )

        contract = Contract(
            user_id=user_id,
            manager_id=manager_id,
            work_contract_id=work_contract_history.work_contract.id,
            modusign_id=modusign_id,
            contract_name=contract_name,
            contract_url=contract_url,
        )

        contract_id = await add_contract(session=session, contract=contract)
        return contract_id

    async def request_contract_by_modusign(
            self,
            user: Users,
    ) -> dict:
        template_response = await modusign_template_service.get_template(template_id=SAMPLE_TEMPLATE_ID)

        document_data = ModuSignGenerator.convert_template_response_to_document_data(
            template_response=template_response,
            user=user
        )

        result = await modusign_document_service.create_document_with_template(document_data=document_data)
        return result

    async def approve_contract(
            self,
            modusign_document_id: str,
            session: AsyncSession,
    ):
        """
        계약을 승인하는 로직
        """

        contract = await find_contract_by_modusign_id(
            modusign_id=modusign_document_id,
            session=session
        )
        if not contract:
            return

        await user_management_service.update_user_role(
            user_id=contract.user_id,
            session=session
        )

