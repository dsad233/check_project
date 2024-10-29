import logging
from typing import List, Dict, Any
from fastapi import HTTPException
from app.core.config import settings
import base64
import aiohttp
from app.schemas.modusign_schemas import TemplateListResponse, TemplateResponse
import json

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
                headers = self.headers.copy()
                
                if isinstance(kwargs.get('data'), aiohttp.FormData):
                    headers.pop('content-type', None)
                else:
                    headers['content-type'] = 'application/json'
                    
                logger.info(f"Making request to {url}")
                logger.info(f"Request headers: {headers}")
                logger.info(f"Request data: {kwargs.get('json') or kwargs.get('data')}")
                
                async with session.request(method, url, headers=headers, **kwargs) as response:
                    response_text = await response.text()
                    logger.info(f"Response status: {response.status}")
                    logger.info(f"Response headers: {response.headers}")
                    logger.info(f"Response body: {response_text}")
                    
                    if response.status >= 400:
                        try:
                            error_data = await response.json()
                            detail = f"API Error: {error_data.get('error', {}).get('name', 'Unknown')} - {error_data.get('error', {}).get('message', error_data)}"
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

    async def upload_file(self, file_content: bytes, filename: str) -> Dict:
        """파일을 먼저 업로드합니다"""
        try:
            form = aiohttp.FormData()
            form.add_field('file',
                        file_content,
                        filename=filename,
                        content_type='application/pdf')

            data = await self._make_request(
                'POST',
                f"{MODUSIGN_BASE_URL}/files",
                data=form
            )
            return data
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    async def create_template(self, template_data: Dict[str, Any]) -> TemplateResponse:
        """템플릿을 생성합니다"""
        try:
            logger.info("=== Making API Request ===")
            logger.info(f"URL: {MODUSIGN_BASE_URL}/templates")
            logger.info(f"Headers: {self.headers}")
            logger.info(f"Request Body: {json.dumps(template_data, indent=2, ensure_ascii=False)}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{MODUSIGN_BASE_URL}/templates",
                    headers=self.headers,
                    json=template_data
                ) as response:
                    response_data = await response.json()
                    logger.info(f"Response Status: {response.status}")
                    logger.info(f"Response Data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                    
                    if response.status >= 400:
                        raise HTTPException(status_code=response.status, detail=str(response_data))
                        
                    return TemplateResponse(**response_data)
                    
        except Exception as e:
            logger.error(f"Error creating template: {str(e)}")
            raise

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
        result = await self._make_request(
            'DELETE',
            f"{MODUSIGN_BASE_URL}/templates/{template_id}"
        )
        return result.get('success', False)
