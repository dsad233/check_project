import logging
from typing import Dict, Any, List
import aiohttp
from app.core.config import settings
from app.exceptions.exceptions import BadRequestError, NotFoundError

logger = logging.getLogger(__name__)

async def create_template(title: str, file_data: Dict[str, str], participants: List[Dict[str, Any]], 
                    requester_inputs: List[Dict[str, Any]] = None, metadatas: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """템플릿을 생성합니다."""
    url = f"{settings.MODUSIGN_BASE_URL}/templates"
    payload = {
        "title": title,
        "file": file_data,
        "participants": participants
    }
    if requester_inputs:
        payload["requesterInputs"] = requester_inputs
    if metadatas:
        payload["metadatas"] = metadatas

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, headers=settings.MODUSIGN_HEADERS) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientResponseError as e:
            logger.error(f"Error creating template: {str(e)}")
            raise BadRequestError(f"템플릿 생성 중 오류 발생: {str(e)}")

async def get_template(template_id: str) -> Dict[str, Any]:
    """특정 ID의 템플릿을 조회합니다."""
    url = f"{settings.MODUSIGN_BASE_URL}/templates/{template_id}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=settings.MODUSIGN_HEADERS) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientResponseError as e:
            if e.status == 404:
                raise NotFoundError(f"템플릿을 찾을 수 없습니다: {template_id}")
            logger.error(f"Error getting template: {str(e)}")
            raise BadRequestError(f"템플릿 조회 중 오류 발생: {str(e)}")

async def update_template(template_id: str, title: str = None, participants: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """템플릿을 업데이트합니다."""
    url = f"{settings.MODUSIGN_BASE_URL}/templates/{template_id}"
    payload = {}
    if title:
        payload["title"] = title
    if participants:
        payload["participants"] = participants
    async with aiohttp.ClientSession() as session:
        try:
            async with session.patch(url, json=payload, headers=settings.MODUSIGN_HEADERS) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientResponseError as e:
            logger.error(f"Error updating template: {str(e)}")
            raise BadRequestError(f"템플릿 업데이트 중 오류 발생: {str(e)}")

async def delete_template(template_id: str) -> int:
    """템플릿을 삭제합니다."""
    url = f"{settings.MODUSIGN_BASE_URL}/templates/{template_id}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.delete(url, headers=settings.MODUSIGN_HEADERS) as response:
                response.raise_for_status()
                return response.status
        except aiohttp.ClientResponseError as e:
            logger.error(f"Error deleting template: {str(e)}")
            raise BadRequestError(f"템플릿 삭제 중 오류 발생: {str(e)}")

async def list_templates(page: int = 1, limit: int = 10) -> Dict[str, Any]:
    """템플릿 목록을 조회합니다."""
    url = f"{settings.MODUSIGN_BASE_URL}/templates?page={page}&limit={limit}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=settings.MODUSIGN_HEADERS) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientResponseError as e:
            logger.error(f"Error listing templates: {str(e)}")
            raise BadRequestError(f"템플릿 목록 조회 중 오류 발생: {str(e)}")

async def create_document_with_template(template_id: str, document: Dict[str, Any]) -> Dict[str, Any]:
    """템플릿으로 새 문서를 생성합니다."""
    url = f"{settings.MODUSIGN_BASE_URL}/documents/request-with-template"
    payload = {
        "templateId": template_id,
        "document": document
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, headers=settings.MODUSIGN_HEADERS) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientResponseError as e:
            logger.error(f"Error creating document with template: {str(e)}")
            raise BadRequestError(f"템플릿으로 문서 생성 중 오류 발생: {str(e)}")