import logging
from typing import Dict
from fastapi import HTTPException
from app.core.config import settings
import base64
import aiohttp
from aiohttp.client_exceptions import ContentTypeError
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
            "authorization": f"Basic {encoded_auth}"
        }

    async def _make_request(self, method: str, url: str, **kwargs) -> Dict:
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    **self.headers,
                    'Content-Type': 'application/json'
                }
                if 'headers' in kwargs:
                    headers.update(kwargs.pop('headers'))
                
                logger.info(f"Making {method} request to: {url}")
                logger.info(f"Headers: {headers}")
                
                async with session.request(method, url, headers=headers, **kwargs) as response:
                    logger.info(f"Response status: {response.status}")
                    
                    if response.status >= 400:
                        response_text = await response.text()
                        logger.error(f"API request failed: {response_text}")
                        try:
                            error_data = await response.json()
                            detail = f"API Error: {error_data.get('error', {}).get('name', 'Unknown')} - {error_data}"
                        except:
                            detail = f"API Error: {response_text}"
                        raise HTTPException(status_code=response.status, detail=detail)
                    
                    if method.upper() == 'DELETE' and response.status in (200, 204):
                        return {"success": True}
                    
                    try:
                        return await response.json()
                    except ContentTypeError:
                        response_text = await response.text()
                        if not response_text:
                            return {"success": True}
                        raise
                
        except aiohttp.ClientError as e:
            logger.error(f"HTTP request failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"HTTP request failed: {str(e)}")

    async def get_templates(self) -> TemplateListResponse:
        """템플릿 목록을 조회합니다"""
        data = await self._make_request(
            'GET',
            f"{MODUSIGN_BASE_URL}/templates"
        )
        return TemplateListResponse(**data)

    async def get_template(self, template_id: str) -> TemplateResponse:
        """템플릿 상세 정보를 조회합니다"""
        data = await self._make_request(
            'GET',
            f"{MODUSIGN_BASE_URL}/templates/{template_id}"
        )
        return TemplateResponse(**data)

    async def delete_template(self, template_id: str) -> bool:
        """템플릿을 삭제합니다"""
        try:
            if not template_id:
                raise ValueError("Template ID is required")
                
            logger.info(f"Deleting template with ID: {template_id}")
            
            # URL에 쿼리 파라미터로 template_id 추가
            result = await self._make_request(
                method='DELETE',
                url=f"{MODUSIGN_BASE_URL}/templates?id={template_id}"
            )
            
            logger.info(f"Delete template response: {result}")
            return result.get('success', False)
            
        except Exception as e:
            logger.error(f"Error in delete_template: {str(e)}")
            raise

    async def update_template_metadata(self, template_id: str, metadata: list) -> Dict:
        """템플릿 메타데이터를 업데이트합니다"""
        try:
            if not template_id:
                raise ValueError("Template ID is required")
            
            logger.info(f"Updating template metadata for ID: {template_id}")
            logger.info(f"Metadata: {metadata}")
            
            # metadata를 객체로 감싸서 전송
            result = await self._make_request(
                'PUT',
                f"{MODUSIGN_BASE_URL}/templates/{template_id}/metadatas",
                json={
                    "metadatas": [{"key": m.key, "value": m.value} for m in metadata]
                }
            )
            
            logger.info(f"Update template metadata response: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in update_template_metadata: {str(e)}")
            raise