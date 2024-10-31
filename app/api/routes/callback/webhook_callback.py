from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.callback_schemas import DocumentAllSigned
from app.service.user_management.contract_service import UserManagementContractService
from app.service.user_management.service import UserManagementService

router = APIRouter(dependencies=[])
user_management_service = UserManagementService()
user_management_contract_service = UserManagementContractService()


class WebhookCallback:
    router = router

    @router.post("/document-all-signed")
    async def request_contract_document_all_signed(
            body: DocumentAllSigned,
            db: AsyncSession = Depends(get_db),
    ):
        if body.event.type != "document_all_signed":
            return {"status": "FAIL", "message": "Invalid event type"}

        document_id = body.document.id
        print(document_id)

webhook_callback = WebhookCallback()