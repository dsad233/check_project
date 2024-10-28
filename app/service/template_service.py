import logging
from typing import List, Dict, Any
from fastapi import HTTPException
from app.core.config import settings
import base64
import aiohttp
from app.schemas.modusign_schemas import TemplateListResponse, TemplateResponse

logger = logging.getLogger(__name__)
MODUSIGN_BASE_URL = "https://api.modusign.co.kr"

class TemplateService:
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
                logger.info(f"Making {method} request to {url}")
                if kwargs.get('json'):
                    logger.info(f"Request payload: {kwargs['json']}")
                
                async with session.request(method, url, headers=self.headers, **kwargs) as response:
                    response_text = await response.text()
                    logger.info(f"Response status: {response.status}")
                    logger.info(f"Response body: {response_text}")
                    
                    if response.status not in [200, 201, 204]:
                        try:
                            error_data = await response.json()
                            detail = error_data.get('message', 'API request failed')
                        except:
                            detail = response_text
                        raise HTTPException(status_code=response.status, detail=detail)
                    
                    if response.status == 204:
                        return {"success": True}
                    return await response.json()
        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def create_template(self, template_data: Dict[str, Any]) -> TemplateResponse:
        """템플릿 생성"""
        data = await self._make_request(
            'POST',
            f"{MODUSIGN_BASE_URL}/templates",
            json=template_data
        )
        return TemplateResponse(**data)

    async def get_templates(self) -> TemplateListResponse:
        """템플릿 목록 조회"""
        try:
            data = await self._make_request(
                'GET',
                f"{MODUSIGN_BASE_URL}/templates"
            )
            logger.info(f"Templates response data: {data}")  # 응답 데이터 로깅
            
            # API 응답 형식에 맞게 변환
            return TemplateListResponse(
                count=data.get('count', 0),
                templates=data.get('templates', [])
            )
        except Exception as e:
            logger.error(f"Error in get_templates: {str(e)}")
            raise

    async def get_template(self, template_id: str) -> TemplateResponse:
        """템플릿 상세 정보 조회"""
        try:
            data = await self._make_request(
                'GET',
                f"{MODUSIGN_BASE_URL}/templates/{template_id}"
            )
            logger.info(f"Template response data: {data}")  # 응답 데이터 로깅
            
            return TemplateResponse(**data)
        except Exception as e:
            logger.error(f"Error in get_template: {str(e)}")
            raise

    async def delete_template(self, template_id: str) -> bool:
        """템플릿 삭제"""
        result = await self._make_request(
            'DELETE',
            f"{MODUSIGN_BASE_URL}/templates/{template_id}"
        )
        return result.get('success', False)
    
    async def create_template_with_file(
        self, 
        title: str, 
        file_data: Dict[str, str], 
        participants: List[Dict[str, Any]], 
        requester_inputs: List[Dict[str, Any]] = None, 
        metadatas: List[Dict[str, str]] = None
    ) -> TemplateResponse:
        """파일과 함께 템플릿을 생성합니다."""
        payload = {
            "title": title,
            "file": file_data,
            "participants": participants
        }
        if requester_inputs:
            payload["requesterInputs"] = requester_inputs
        if metadatas:
            payload["metadatas"] = metadatas

        data = await self._make_request(
            'POST',
            f"{MODUSIGN_BASE_URL}/templates",
            json=payload
        )
        return TemplateResponse(**data)

    async def update_template(
        self, 
        template_id: str, 
        title: str = None, 
        participants: List[Dict[str, Any]] = None
    ) -> TemplateResponse:
        """템플릿을 업데이트합니다."""
        payload = {}
        if title:
            payload["title"] = title
        if participants:
            payload["participants"] = participants
            
        data = await self._make_request(
            'PATCH',
            f"{MODUSIGN_BASE_URL}/templates/{template_id}",
            json=payload
        )
        return TemplateResponse(**data)

    async def list_templates(self, page: int = 1, limit: int = 10) -> TemplateListResponse:
        """템플릿 목록을 페이지네이션과 함께 조회합니다."""
        data = await self._make_request(
            'GET',
            f"{MODUSIGN_BASE_URL}/templates?page={page}&limit={limit}"
        )
        return TemplateListResponse(**data)