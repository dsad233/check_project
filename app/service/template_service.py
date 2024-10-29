import logging
from typing import Dict
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
            "authorization": f"Basic {encoded_auth}"
        }

    async def _make_request(self, method: str, url: str, **kwargs) -> Dict:
        try:
            async with aiohttp.ClientSession() as session:
                # 기본 헤더 설정
                headers = {
                    **self.headers,
                    'Content-Type': 'application/json'
                }
                
                # 추가 헤더가 있으면 업데이트
                if 'headers' in kwargs:
                    headers.update(kwargs.pop('headers'))
                
                # 요청 정보 로깅
                logger.info(f"Making {method} request to: {url}")
                logger.info(f"Headers: {headers}")
                logger.info(f"Request data: {kwargs.get('json')}")
                
                async with session.request(method, url, headers=headers, **kwargs) as response:
                    response_text = await response.text()
                    logger.info(f"Response status: {response.status}")
                    logger.info(f"Response body: {response_text}")
                    
                    if response.status >= 400:
                        try:
                            error_data = await response.json()
                            detail = f"API Error: {error_data.get('error', {}).get('name', 'Unknown')} - {error_data}"
                        except:
                            detail = f"API Error: {response_text}"
                        logger.error(f"API request failed: {detail}")
                        raise HTTPException(status_code=response.status, detail=detail)
                    
                    if response.status == 204:
                        return {"success": True}
                        
                    return await response.json()
                
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
            # 요청 데이터 준비 - 배열 형태로 직접 전송
            request_data = [str(template_id)]  # 객체가 아닌 배열로 직접 전송
            
            logger.info(f"Template ID: {template_id}")
            logger.info(f"Request data: {request_data}")
            
            # API 요청
            result = await self._make_request(
                method='DELETE',
                url=f"{MODUSIGN_BASE_URL}/templates",
                json=request_data  # 배열을 직접 전송
            )
            logger.info(f"Delete template result: {result}")
            return result.get('success', False)
            
        except Exception as e:
            logger.error(f"Error in delete_template: {str(e)}")
            raise
