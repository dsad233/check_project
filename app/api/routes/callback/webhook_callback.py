from fastapi import APIRouter, Depends, status
from fastapi.params import Annotated, Body

from app.dependencies.user_management import get_user_management_contract_service
from app.schemas.callback_schemas import DocumentAllSigned
from app.service.user_management.contract_service import UserManagementContractService

router = APIRouter(dependencies=[])


class WebhookCallback:
    router = router

    @router.post("/document-all-signed", status_code=status.HTTP_204_NO_CONTENT)
    async def request_contract_document_all_signed(
            body: Annotated[DocumentAllSigned, Body(...)],
            contract_service: Annotated[UserManagementContractService, Depends(get_user_management_contract_service)]
    ):
        if body.event.type != "document_all_signed":
            return {"status": "FAIL", "message": "Invalid event type"}

        result = await contract_service.callback_by_modusign(modusign_document_id=body.document.id)

        if not result:
            return

webhook_callback = WebhookCallback()