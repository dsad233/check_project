from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dto.response_dto import ResponseDTO
from app.core.database import get_db
from app.cruds.user_management.document_crud import find_by_id_with_documents, add_documents, \
    hard_delete_document, add_send_document_history, find_send_document_history_by_request_user_id, \
    find_send_document_history_by_user_id, patch_document_send_history_status, delete_send_document_history
from app.enums.user_management import DocumentSendStatus
from app.middleware.tokenVerify import validate_token, get_current_user
from app.models.users.users_model import Users
from app.schemas.user_management_document_schemas import ResponseUserDocuments, RequestAddDocuments, \
    RequestRemoveDocument, \
    ResponseAddedDocuments, RequestSendDocument, ResponseSendDocumentHistoryDto, ResponseDocumentSendHistoryRequestsDto, \
    RequestApproveSendDocument, RequestRejectSendDocument, RequestCancelSendDocument

router = APIRouter(dependencies=[Depends(validate_token)])


class UserManagementDocument:
    router = router

    @router.get("", response_model=ResponseDTO[ResponseUserDocuments])
    async def get_user_documents(
            user_id: int,
            db: AsyncSession = Depends(get_db),
            current_user: Users = Depends(get_current_user),
    ):
        try:
            user = await find_by_id_with_documents(session=db, user_id=user_id)
            if not user:
                raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

            data = ResponseUserDocuments.build(user.documents)

            return ResponseDTO(
                status="SUCCESS",
                message="성공적으로 문서를 가져왔습니다.",
                data=data,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("", response_model=ResponseDTO[ResponseAddedDocuments])
    async def add_user_document(
            request_add_documents: RequestAddDocuments,
            db: AsyncSession = Depends(get_db),
            current_user: Users = Depends(get_current_user),
    ):
        documents = [
            {
                "user_id": request_add_documents.user_id,
                "document_name": document.document_name,
            }
            for document in request_add_documents.documents
        ]

        add_document_ids = await add_documents(session=db, documents=documents)
        data = ResponseAddedDocuments.build(document_ids=add_document_ids)

        return ResponseDTO(
            status="SUCCESS",
            message="성공적으로 문서를 추가했습니다.",
            data=data
        )

    @router.delete("", response_model=ResponseDTO)
    async def delete_user_document(
            request_remove_document: RequestRemoveDocument,
            db: AsyncSession = Depends(get_db),
            current_user: Users = Depends(get_current_user),
    ):
        try:
            await hard_delete_document(
                session=db,
                user_id=request_remove_document.user_id,
                document_id=request_remove_document.document_id
            )

            return ResponseDTO(
                status="SUCCESS",
                message="성공적으로 문서를 삭제했습니다."
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/send/{user_id}", response_model=ResponseDTO[ResponseDocumentSendHistoryRequestsDto])
    async def get_send_document_requests(
            user_id: int,
            db: AsyncSession = Depends(get_db),
            current_user: Users = Depends(get_current_user),
    ):
        document_send_histories = await find_send_document_history_by_user_id(
            session=db,
            user_id=user_id
        )
        data = ResponseDocumentSendHistoryRequestsDto.build(document_send_histories=document_send_histories)

        return ResponseDTO(
            status="SUCCESS",
            message="성공적으로 문서 요청을 가져왔습니다.",
            data=data
        )



    @router.post("/send", response_model=ResponseDTO[ResponseSendDocumentHistoryDto])
    async def send_document(
            request_send_document: RequestSendDocument,
            db: AsyncSession = Depends(get_db),
            current_user: Users = Depends(get_current_user),
    ):
        request_send_document_dict = request_send_document.model_dump()
        inserted_send_document_history_id = await add_send_document_history(
            session=db,
            send_document_history_dict=request_send_document_dict
        )

        data = ResponseSendDocumentHistoryDto.build(
            document_send_history_id=inserted_send_document_history_id
        )

        return ResponseDTO(
            status="SUCCESS",
            message="성공적으로 문서 요청을 전송했습니다.",
            data=data
        )

    @router.patch("/approve", response_model=ResponseDTO)
    async def approve_send_document(
            request_approve_send_document: RequestApproveSendDocument,
            db: AsyncSession = Depends(get_db),
            current_user: Users = Depends(get_current_user),
    ):
        result = await patch_document_send_history_status(
            session=db,
            document_send_history_id=request_approve_send_document.document_send_history_id,
            status=DocumentSendStatus.APPROVE
        )

        if not result:
            raise HTTPException(status_code=400, detail="승인할 문서가 존재하지 않습니다.")

        return ResponseDTO(
            status="SUCCESS",
            message="성공적으로 문서 전달을 승인했습니다.",
        )

    @router.patch("/reject", response_model=ResponseDTO)
    async def reject_send_document(
            request_reject_send_document: RequestRejectSendDocument,
            db: AsyncSession = Depends(get_db),
            current_user: Users = Depends(get_current_user),
    ):
        result = await patch_document_send_history_status(
            session=db,
            document_send_history_id=request_reject_send_document.document_send_history_id,
            status=DocumentSendStatus.REJECT
        )

        if not result:
            raise HTTPException(status_code=400, detail="반려할 문서가 존재하지 않습니다.")

        return ResponseDTO(
            status="SUCCESS",
            message="성공적으로 문서 전달을 반려했습니다.",
        )

    @router.delete("/cancel", response_model=ResponseDTO)
    async def cancel_send_document(
            requset_cancel_send_document: RequestCancelSendDocument,
            db: AsyncSession = Depends(get_db),
            current_user: Users = Depends(get_current_user),
    ):
        result = await delete_send_document_history(
            session=db,
            document_send_history_id=requset_cancel_send_document.document_send_history_id,
            user_id=requset_cancel_send_document.user_id
        )

        if not result:
            return ResponseDTO(
                status="SUCCESS",
                message="취소할 문서가 존재하지 않습니다.",
            )

        return ResponseDTO(
            status="SUCCESS",
            message="성공적으로 문서 전달을 취소했습니다.",
        )



user_management_document = UserManagementDocument()