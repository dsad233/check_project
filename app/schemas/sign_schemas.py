from pydantic import BaseModel, Field
from typing import List, Optional

class ParticipantMapping(BaseModel):
    role: str
    name: str
    signingMethod: dict = Field(..., example={
        "type": "EMAIL",
        "value": "modu.kim@modusign.co.kr"
    })
    excluded: Optional[bool] = None
    signingDuration: Optional[int] = None
    locale: Optional[str] = None
    verification: Optional[dict] = None
    attachmentRequests: Optional[List[dict]] = None

class RequesterInputMapping(BaseModel):
    dataLabel: str
    value: str

class Metadata(BaseModel):
    key: str
    value: str

class CreateDocumentRequest(BaseModel):
    templateId: str
    document: dict = Field(..., example={
        "title": "2020_근로계약서_홍길동",
        "participantMappings": List[ParticipantMapping],
        "requesterInputMappings": Optional[List[RequesterInputMapping]],
        "metadatas": Optional[List[Metadata]]
    })

class CreateDocumentResponse(BaseModel):
    id: str
    title: str
    status: str
    participants: List[dict]
    createdAt: str
    updatedAt: str

class EmbeddedSignLinkResponse(BaseModel):
    embeddedUrl: str

class WebhookEvent(BaseModel):
    type: str

class WebhookDocument(BaseModel):
    id: str

class WebhookRequester(BaseModel):
    email: str

class CreateSignWebhookRequest(BaseModel):
    requester: WebhookRequester
    event: WebhookEvent
    document: WebhookDocument

class DocumentListRequest(BaseModel):
    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1, le=100)

class DocumentListResponse(BaseModel):
    data: List[dict]
    total_count: int