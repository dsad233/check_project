from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.user_management import get_user_management_contract_service
from app.schemas.callback_schemas import DocumentAllSigned
from app.service.user_management.contract_service import UserManagementContractService
from app.service.user_management.service import UserManagementService

router = APIRouter(dependencies=[])


class WebhookCallback:
    router = router

    @router.post("/document-all-signed", status_code=status.HTTP_204_NO_CONTENT)
    async def request_contract_document_all_signed(
            body: DocumentAllSigned,
            contract_service: UserManagementContractService = Depends(get_user_management_contract_service),
            db: AsyncSession = Depends(get_db),
    ):
        if body.event.type != "document_all_signed":
            return {"status": "FAIL", "message": "Invalid event type"}

        result = await contract_service.approve_contract(
            modusign_document_id=body.document.id,
            session=db
        )

        if not result:
            return

webhook_callback = WebhookCallback()