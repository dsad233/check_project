from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users.users_model import Users
from app.service.template_service import TemplateService as ModusignTemplateService
from app.service.document_service import DocumentService as ModusignDocumentService
from app.service.user_management.service import UserManagementService
from app.utils.modusign_utils import ModuSignGenerator

modusign_template_service = ModusignTemplateService()
modusign_document_service = ModusignDocumentService()
user_management_service = UserManagementService()

SAMPLE_TEMPLATE_ID = "e7193300-96da-11ef-8b54-adaae74d0aa0"


class UserManagementContractService:
    async def create_contract(
            self,
            user_id: int,
            # work_contract_history_id: int,
            session: AsyncSession,
    ):
        user = await user_management_service.get_user(user_id=user_id, session=session)
        await self.request_contract_by_modusign(user=user)

        # return

    async def request_contract_by_modusign(
            self,
            user: Users,
    ):
        template_response = await modusign_template_service.get_template(template_id=SAMPLE_TEMPLATE_ID)

        document_data = ModuSignGenerator.convert_template_response_to_document_data(
            template_response=template_response,
            user=user
        )

        result = await modusign_document_service.create_document_with_template(document_data=document_data)
        print(result)

        return result