from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.cruds.user_management.work_contract_crud import find_user_by_user_id
from app.cruds.users.users_crud import find_by_email, add_user
from app.enums.modusign import SIGNINGMETHOD_OBJECT_TYPE
from app.enums.users import Role
from app.models.users.users_model import Users
from app.schemas.modusign_schemas import TemplateResponse, SigningMethod
# from app.service.document_service import DocumentService as ModusignDocumentService
# from app.service.template_service import TemplateService as ModusignTemplateService
#
# modusign_template_service = ModusignTemplateService()
# modusign_document_service = ModusignDocumentService()

# SAMPLE_TEMPLATE_ID = "4f1a7e70-9693-11ef-890d-f93d146ab6ae"
# SAMPLE_TEMPLATE_ID = "8bdac290-96c8-11ef-8b54-adaae74d0aa0"


class UserManagementService:
    async def add_user(
            self,
            user: Users,
            session: AsyncSession,
    ):
        # Check if user already exists
        existing_user = await find_by_email(session=session, email=user.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        # Add user
        created_user = await add_user(session=session, user=user)
        return created_user

    async def get_user(
            self,
            user_id: int,
            session: AsyncSession
    ):
        user = await find_user_by_user_id(session=session, user_id=user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    async def update_user_role(
            self,
            user_id: int,
            session: AsyncSession,
            role: Role = Role.EMPLOYEE,
    ) -> int:
        user = await self.get_user(user_id=user_id, session=session)
        user.role = role

        await session.flush()
        await session.commit()

        return user.id

    # async def register_user(
    #         self,
    #         user: Users,
    #         session: AsyncSession
    # ):
    #     # Add user
    #     created_user = await self.add_user(session=session, user=user)
    #
    #     get_template_response = await modusign_template_service.get_template(template_id=SAMPLE_TEMPLATE_ID)
    #
    #     signing_method = SigningMethod(
    #         type=SIGNINGMETHOD_OBJECT_TYPE.KAKAO,
    #         value=user.phone_number.replace("-", "")
    #     )
    #
    #     document_data = self.convert_template_response_to_document_data(
    #         template_response=get_template_response,
    #         signing_method=signing_method,
    #         user_name=created_user.name
    #     )
    #
    #     create_document_with_template_response = await modusign_document_service.create_document_with_template(
    #         document_data=document_data
    #     )
    #
    #     print(create_document_with_template_response)
    #
    #     return created_user
    #
    #
    # def convert_template_response_to_document_data(
    #         self,
    #         template_response: TemplateResponse,
    #         signing_method: SigningMethod,
    #         user_name: str
    # ) -> dict:
    #     return {
    #         "templateId": template_response.id,
    #         "document": {
    #             "title": template_response.title,
    #             "participantMappings": [
    #                 {
    #                     "signingMethod": signing_method.to_dict(),
    #                     "role": participant.role,
    #                     "name": user_name
    #                 }
    #                 for participant in template_response.participants
    #             ],
    #             "requesterInputMappings": [
    #                 {
    #                     "dataLabel": "USER_NAME",
    #                     "value": user_name
    #                 }
    #             ]
    #         }
    #     }

