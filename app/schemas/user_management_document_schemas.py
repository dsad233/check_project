from pydantic import BaseModel

from app.models.users.users_document_model import Document, DocumentSendHistory
from app.models.users.users_model import Users


# ==================== Request ====================

class AddDocumentDto(BaseModel):
    document_name: str

class RequestAddDocuments(BaseModel):
    user_id: int
    documents: list[AddDocumentDto]

class RequestRemoveDocument(BaseModel):
    user_id: int
    document_id: int

class RequestSendDocument(BaseModel):
    user_id: int
    request_user_id: int
    document_id: int

class BaseRequestSendDocument(BaseModel):
    document_send_history_id: int


class RequestApproveSendDocument(BaseRequestSendDocument):
    user_id: int
    request_user_id: int

class RequestRejectSendDocument(BaseRequestSendDocument):
    user_id: int
    request_user_id: int

class RequestCancelSendDocument(BaseRequestSendDocument):
    user_id: int

# ==================== Response ====================

class DocumentDto(BaseModel):
    document_id: int
    document_name: str

    @classmethod
    def build(cls, document: Document):
        return cls(document_id=document.id, document_name=document.document_name)


class RequestUserDto(BaseModel):
    request_user_id: int
    request_user_name: str

    @classmethod
    def build(cls, request_user: Users):
        return cls(
            request_user_id=request_user.id,
            request_user_name=request_user.name
        )


class AddedDocumentDto(BaseModel):
    document_id: int

    @classmethod
    def build(cls, document_id: int):
        return cls(document_id=document_id)


class ResponseUserDocuments(BaseModel):
    documents: list[DocumentDto]

    @classmethod
    def build(cls, documents: list[Document]):
        return cls(
            documents=[
                DocumentDto.build(document=document)
                for document in documents
            ]
        )

class ResponseAddedDocuments(BaseModel):
    documents: list[AddedDocumentDto]

    @classmethod
    def build(cls, document_ids: list[int]):
        return cls(
            documents=[
                AddedDocumentDto.build(document_id=document_id)
                for document_id in document_ids
            ]
        )

class ResponseSendDocumentHistoryDto(BaseModel):
    document_send_history_id: int

    @classmethod
    def build(cls, document_send_history_id: int):
        return cls(document_send_history_id=document_send_history_id)

class DocumentSendHistoryRequestDto(BaseModel):
    document_send_history_id: int
    document: DocumentDto
    request_user: RequestUserDto
    created_at: str
    status: str

    @classmethod
    def build(cls, document_send_history: DocumentSendHistory):
        return cls(
            document_send_history_id=document_send_history.id,
            document=DocumentDto.build(document=document_send_history.document),
            request_user=RequestUserDto.build(request_user=document_send_history.request_user),
            created_at=document_send_history.created_at.strftime("%Y-%m-%d"),
            status=document_send_history.status.value
        )

class ResponseDocumentSendHistoryRequestsDto(BaseModel):
    document_send_histories: list[DocumentSendHistoryRequestDto]

    @classmethod
    def build(cls, document_send_histories: list[DocumentSendHistory]):
        return cls(
            document_send_histories=[
                DocumentSendHistoryRequestDto.build(document_send_history=send_document_history)
                for send_document_history in document_send_histories
            ]
        )
