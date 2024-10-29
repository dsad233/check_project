import aiohttp
import logging
import base64
import json
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
        logger.info("ModuSign service initialized")

    async def _make_request(self, method: str, url: str, **kwargs) -> Dict:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, headers=self.headers, **kwargs) as response:
                    response_text = await response.text()
                    logger.info(f"Response status: {response.status}")
                    logger.info(f"Response headers: {response.headers}")
                    logger.info(f"Response body: {response_text}")
                    
                    if response.status not in [200, 201, 204]:
                        try:
                            error_data = await response.json()
                            detail = f"API Error: {error_data.get('type', 'UNKNOWN')} - {error_data.get('title', error_data)}"
                        except:
                            detail = f"API Error: {response_text}"
                        raise HTTPException(status_code=response.status, detail=detail)
                    
                    return await response.json()
                    
        except aiohttp.ClientError as e:
            raise HTTPException(status_code=500, detail=f"HTTP request failed: {str(e)}")

    async def get_documents(self) -> Dict:
        """문서 목록을 조회합니다"""
        try:
            data = await self._make_request(
                'GET',
                f"{MODUSIGN_BASE_URL}/documents"
            )
            return {
                'data': data.get('documents', []),
                'total_count': data.get('count', 0)
            }
        except Exception as e:
            logger.error(f"Error getting documents: {str(e)}")
            raise

    async def create_document_with_template(
        self, template_id: str, document: Dict[str, Any]
    ) -> CreateDocumentResponse:
        try:
            data = await self._make_request(
                'POST',
                f"{MODUSIGN_BASE_URL}/documents/request-with-template",
                json={
                    "templateId": template_id,
                    "document": document
                }
            )
            return CreateDocumentResponse(
                document_id=data['id'],
                participant_id=data['participants'][0]['id'] if data.get('participants') else None,
                embedded_url=None  # 서명 URL은 별도 API 호출로 받아야 함
            )
        except Exception as e:
            logger.error(f"Error in create_document_with_template: {str(e)}")
            raise

    async def request_document_signature(
        self, document_id: str
    ) -> EmbeddedSignLinkResponse:
        try:
            data = await self._make_request(
                'GET',
                f"{MODUSIGN_BASE_URL}/documents/{document_id}/embedded-view"
            )
            return EmbeddedSignLinkResponse(embeddedUrl=data['embeddedUrl'])
        except Exception as e:
            logger.error(f"Error in request_document_signature: {str(e)}")
            raise

    async def delete_document(self, document_id: str) -> bool:
        try:
            result = await self._make_request(
                'DELETE',
                f"{MODUSIGN_BASE_URL}/documents/{document_id}"
            )
            return result.get('success', False)
        except Exception as e:
            logger.error(f"Error in delete_document: {str(e)}")
            raise

    async def get_template_details(self, template_id: str) -> Dict[str, Any]:
        """템플릿 상세 정보를 조회합니다."""
        try:
            return await self._make_request(
                'GET',
                f"{MODUSIGN_BASE_URL}/templates/{template_id}"
            )
        except Exception as e:
            logger.error(f"Error in get_template_details: {str(e)}")
            raise

    async def create_document(self, document_data: Dict[str, Any]) -> Dict:
        """문서를 생성합니다"""
        data = await self._make_request(
            'POST',
            f"{MODUSIGN_BASE_URL}/documents",
            json=document_data
        )
        return data
