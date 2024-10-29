from typing import List, Optional
from pydantic import BaseModel, Field

class SigningMethod(BaseModel):
    type: str
    value: str

class ParticipantMapping(BaseModel):
    role: str
    name: str
    signingMethod: SigningMethod

class Metadata(BaseModel):
    key: str
    value: str

class RequesterInputMapping(BaseModel):
    key: str
    value: str

class DocumentContent(BaseModel):
    title: str
    participantMappings: List[ParticipantMapping]
    requesterInputMappings: List[RequesterInputMapping]
    metadatas: List[Metadata]

class DocumentListRequest(BaseModel):
    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1, le=100)

class CreateDocumentRequest(BaseModel):
    templateId: str
    document: DocumentContent

class Document(BaseModel):
    id: str
    title: str
    status: str
    created_at: str
    updated_at: str
    participants: Optional[List[dict]] = None
    metadatas: Optional[List[dict]] = None

class DocumentListResponse(BaseModel):
    data: List[Document]
    total_count: int

class CreateDocumentResponse(BaseModel):
    document_id: str | None = None
    participant_id: str | None = None
    embedded_url: str | None = None

class EmbeddedSignLinkResponse(BaseModel):
    embeddedUrl: str