from pydantic import BaseModel

from app.models.users.users_document_model import Document


# ==================== Request ====================

class AddDocumentDto(BaseModel):
    document_name: str

class RequestAddDocuments(BaseModel):
    user_id: int
    documents: list[AddDocumentDto]

class RequestRemoveDocument(BaseModel):
    user_id: int
    document_id: int

# ==================== Response ====================

class DocumentDto(BaseModel):
    document_id: int
    document_name: str

    @classmethod
    def build(cls, document: Document):
        return cls(document_id=document.id, document_name=document.document_name)


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
