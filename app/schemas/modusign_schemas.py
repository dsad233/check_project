from typing import List, Optional
from pydantic import BaseModel, Field

class DocumentListRequest(BaseModel):
    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1, le=100)

class CreateDocumentRequest(BaseModel):
    """문서 생성 요청 스키마"""
    templateId: str
    document: dict = Field(..., example={
        "title": "근로계약서",
        "participantMappings": [
            {
                "role": "직원",
                "name": "홍길동",
                "signingMethod": {
                    "type": "EMAIL",
                    "value": "employee@example.com"
                }
            }
        ],
        "requesterInputMappings": [
            {
                "key": "employee_name",
                "value": "홍길동"
            }
        ],
        "metadatas": [
            {
                "key": "department",
                "value": "개발팀"
            }
        ]
    })

class Document(BaseModel):
    """문서 정보 스키마"""
    id: str
    title: str
    status: str
    created_at: str
    updated_at: str
    participants: Optional[List[dict]] = None
    metadatas: Optional[List[dict]] = None

class DocumentListResponse(BaseModel):
    """문서 목록 응답 스키마"""
    data: List[Document]
    total_count: int

class CreateDocumentResponse(BaseModel):
    document_id: str | None = None
    participant_id: str | None = None
    embedded_url: str | None = None

class EmbeddedSignLinkResponse(BaseModel):
    embeddedUrl: str