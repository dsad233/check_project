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
        async with aiohttp.ClientSession() as session:
            headers = self.headers.copy()
            
            # form-data 요청인 경우에만 content-type 헤더 제거
            if 'data' in kwargs and isinstance(kwargs['data'], aiohttp.FormData):
                headers.pop('content-type', None)
            # JSON 요청인 경우 content-type 유지
            elif 'json' in kwargs:
                headers['content-type'] = 'application/json'
            
            try:
                async with session.request(method, url, headers=headers, **kwargs) as response:
                    response_text = await response.text()
                    logger.info(f"API Response: {response_text}")
                    
                    if response.status >= 400:
                        try:
                            error_data = json.loads(response_text)
                            detail = f"API Error: {error_data.get('type', 'Unknown')} - {error_data}"
                        except json.JSONDecodeError:
                            detail = f"API Error: {response_text}"
                        raise HTTPException(status_code=response.status, detail=detail)
                    
                    return json.loads(response_text) if response_text else {}
                    
            except aiohttp.ClientError as e:
                logger.error(f"HTTP request failed: {str(e)}")
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

    async def create_document(self, document_data: Dict[str, Any]) -> Dict:
        """일반 서명 요청"""
        try:
            # 파일 데이터 읽기
            file_content = await document_data['file'].read()
            file_base64 = base64.b64encode(file_content).decode('utf-8')
            
            # 파일 확장자 추출
            filename = document_data['file'].filename
            extension = filename.split('.')[-1].lower()
            
            # API 요청 데이터 구성
            request_data = {
                "title": str(document_data['title']),
                "file": {
                    "name": filename,
                    "base64": file_base64,
                    "extension": extension,
                    "contentType": document_data['file'].content_type
                },
                "participants": [{
                    "name": document_data['participants']['name'],
                    "role": "SIGNER",
                    "signingOrder": 1,
                    "signingMethod": document_data['participants']['signingMethod']
                }]
            }
            
            logger.info(f"Sending request with file name: {filename}, extension: {extension}")
            
            # JSON 형식으로 요청
            data = await self._make_request(
                'POST',
                f"{MODUSIGN_BASE_URL}/documents",
                json=request_data
            )
            return data
        except Exception as e:
            logger.error(f"Error in create_document: {str(e)}")
            raise

    async def create_document_with_template(self, document_data: Dict[str, Any]) -> Dict:
        """템플릿으로 서명 요청"""
        try:
            data = await self._make_request(
                'POST',
                f"{MODUSIGN_BASE_URL}/documents/request-with-template",
                json=document_data
            )
            return data
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

    async def get_document_details(self, document_id: str) -> Dict[str, Any]:
        """문서 상세 정보를 조회합니다."""
        try:
            return await self._make_request(
                'GET',
                f"{MODUSIGN_BASE_URL}/documents/{document_id}"
            )
        except Exception as e:
            logger.error(f"Error in get_document_details: {str(e)}")
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

    async def get_participant_fields(self, document_id: str) -> Dict[str, Any]:
        """서명자 입력란 조회"""
        try:
            return await self._make_request(
                'GET',
                f"{MODUSIGN_BASE_URL}/documents/{document_id}/participant-fields"
            )
        except Exception as e:
            logger.error(f"Error in get_participant_fields: {str(e)}")
            raise