from typing import List, Optional
from pydantic import BaseModel, Field

# 공통 컴포넌트
class SigningMethod(BaseModel):
    type: str = Field(..., description="서명 방법 타입 (EMAIL)")
    value: str = Field(..., description="이메일 주소")

class Metadata(BaseModel):
    key: str = Field(..., description="메타데이터 키")
    value: str = Field(..., description="메타데이터 값")

class TemplateElement(BaseModel):
    type: str = Field(..., description="필드 타입 (SIGNATURE, TEXTFIELD, DATEFIELD 등)")
    role: str = Field(..., description="참가자 역할")
    x: int = Field(..., description="X 좌표")
    y: int = Field(..., description="Y 좌표")
    width: int = Field(..., description="너비")
    height: int = Field(..., description="높이")
    page: int = Field(..., description="페이지 번호") 
    required: bool = Field(True, description="필수 여부")
    placeholder: Optional[str] = Field(None, description="입력 필드 안내 텍스트")

# 문서 관련 스키마
class DocumentListRequest(BaseModel):
    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1, le=100)

class ParticipantMapping(BaseModel):
    name: str = Field(..., description="참가자 이름")
    role: str = Field(..., description="참가자 역할")
    signingMethod: SigningMethod = Field(..., description="서명 방법")

class RequesterInputMapping(BaseModel):
    key: str = Field(..., description="입력 필드 키")
    value: str = Field(..., description="입력 필드 값")
    dataLabel: str = Field(..., description="입력 필드 레이블")

class DocumentContent(BaseModel):
    title: str = Field(..., description="문서 제목")
    metadatas: List[Metadata] = Field(default_factory=list, description="메타데이터 목록")
    participantMappings: List[ParticipantMapping] = Field(..., description="참가자 매핑 목록")
    requesterInputMappings: List[RequesterInputMapping] = Field(..., description="요청자 입력 매핑 목록")

class CreateDocumentRequest(BaseModel):
    templateId: str = Field(..., description="템플릿 ID")
    document: DocumentContent = Field(..., description="문서 내용")

class Document(BaseModel):
    id: str
    title: str
    status: str
    createdAt: str
    updatedAt: str
    participants: Optional[List[dict]] = None
    metadatas: Optional[List[dict]] = None

class DocumentListResponse(BaseModel):
    documents: List[Document]
    total_count: int

class CreateDocumentResponse(BaseModel):
    document_id: str
    participant_id: Optional[str] = None
    embedded_url: Optional[str] = None

class EmbeddedSignLinkResponse(BaseModel):
    embeddedUrl: str

# 템플릿 관련 스키마
class FileInfo(BaseModel):
    downloadUrl: Optional[str] = None
    name: Optional[str] = None
    size: Optional[int] = None
    contentType: Optional[str] = None

class SigningMethod(BaseModel):
    type: str
    value: str

class Participant(BaseModel):
    role: str
    signingOrder: int
    name: Optional[str] = None
    signingMethod: Optional[SigningMethod] = None

class FieldPosition(BaseModel):
    type: str
    role: str
    x: int
    y: int
    width: int
    height: int
    pageNumber: int
    required: bool = True
    placeholder: Optional[str] = None

class Template(BaseModel):
    id: str
    title: str
    metadatas: List[dict] = []
    file: FileInfo
    participants: List[Participant] = []
    requesterInputs: List[dict] = []
    fieldPositions: Optional[List[FieldPosition]] = None
    createdAt: str
    updatedAt: str

class TemplateResponse(BaseModel):
    id: str
    title: str
    metadatas: List[dict] = []
    file: FileInfo
    participants: List[Participant] = []
    requesterInputs: List[dict] = []
    fieldPositions: Optional[List[FieldPosition]] = None
    createdAt: str
    updatedAt: str

class TemplateListResponse(BaseModel):
    count: int
    templates: List[Template]

    class Config:
        from_attributes = True

class RequesterInputField(BaseModel):
    type: str
    key: str
    name: str
    required: bool = True
    options: Optional[List[str]] = None

class RequesterInput(BaseModel):
    fields: List[RequesterInputField]
