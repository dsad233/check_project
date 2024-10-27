from fastapi import APIRouter, Depends, HTTPException, status

from app.common.dto.response_dto import ResponseDTO
from app.core.database import async_session
from app.cruds.user_management.user_management_document_crud import find_by_id_with_documents, add_documents, \
    hard_delete_document
from app.middleware.tokenVerify import validate_token, get_current_user
from app.models.users.users_model import Users
from app.schemas.user_management_document_schemas import ResponseUserDocuments, RequestAddDocuments, RequestRemoveDocument, \
    ResponseAddedDocuments

router = APIRouter(dependencies=[Depends(validate_token)])
db = async_session()

class UserManagementDocument:
    router = router

    @router.get("", response_model=ResponseDTO[ResponseUserDocuments])
    async def get_user_documents(
        user_id: int,
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
        current_user: Users = Depends(get_current_user),
    ):
        documents = [
            {
                "user_id": request_add_documents.id,
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


user_management_document = UserManagementDocument()