import aiohttp
import logging
import base64
from fastapi import HTTPException
from typing import List, Tuple, Dict, Any
from app.core.config import settings
from app.schemas.modusign_schemas import (
    DocumentListRequest,
    CreateDocumentRequest,
    CreateDocumentResponse,
    EmbeddedSignLinkResponse,
    Document
)

logger = logging.getLogger(__name__)
MODUSIGN_BASE_URL = "https://api.modusign.co.kr"

class DocumentService:
    def __init__(self):
        if not settings.MODUSIGN_API_KEY or not settings.MODUSIGN_USER_EMAIL:
            raise ValueError("MODUSIGN_API_KEY and MODUSIGN_USER_EMAIL must be set")
            
        auth_string = f"{settings.MODUSIGN_USER_EMAIL}:{settings.MODUSIGN_API_KEY}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Basic {encoded_auth}"
        }

    async def _make_request(self, method: str, url: str, **kwargs) -> Dict:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, headers=self.headers, **kwargs) as response:
                    if response.status == 204:  # DELETE 요청 성공
                        return {"success": True}
                        
                    response_text = await response.text()
                    logger.info(f"API Response: {response_text}")  # 응답 로깅 추가
                    
                    if response.status != 200:
                        try:
                            error_data = await response.json()
                            detail = error_data.get('message', 'API request failed')
                        except:
                            detail = response_text
                        raise HTTPException(status_code=response.status, detail=detail)
                    
                    return await response.json()
        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_documents(
        self, request: DocumentListRequest, offset: int, limit: int
    ) -> Tuple[List[Document], int]:
        data = await self._make_request('GET', f"{MODUSIGN_BASE_URL}/documents")
        documents = [Document(**doc) for doc in data.get('documents', [])]
        total_count = data.get('total_count', 0)
        return documents, total_count

    async def create_document_with_template(
        self, request: CreateDocumentRequest
    ) -> CreateDocumentResponse:
        payload = {
            "templateId": request.templateId,
            "document": request.document.model_dump()  # Pydantic v2 사용
        }
        logger.info(f"Create document payload: {payload}")  # 요청 페이로드 로깅
        
        data = await self._make_request(
            'POST',
            f"{MODUSIGN_BASE_URL}/documents/request-with-template",
            json=payload
        )
        
        return CreateDocumentResponse(
            document_id=data.get('id'),
            participant_id=data.get('participants', [{}])[0].get('id') if data.get('participants') else None,
            embedded_url=None
        )

    async def request_document_signature(
        self, document_id: str
    ) -> EmbeddedSignLinkResponse:
        data = await self._make_request(
            'GET',
            f"{MODUSIGN_BASE_URL}/documents/{document_id}/embedded-view"
        )
        return EmbeddedSignLinkResponse(embeddedUrl=data['embeddedUrl'])

    async def delete_document(self, document_id: str) -> bool:
        result = await self._make_request(
            'DELETE',
            f"{MODUSIGN_BASE_URL}/documents/{document_id}"
        )
        return result.get('success', False)

    async def get_document_details(self, document_id: str) -> Dict[str, Any]:
        return await self._make_request(
            'GET',
            f"{MODUSIGN_BASE_URL}/documents/{document_id}"
        )