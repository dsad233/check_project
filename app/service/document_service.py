import aiohttp
import logging,sys
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List, Tuple, Dict, Any
from app.core.config import settings
from app.schemas.modusign_schemas import (
    DocumentListRequest,
    CreateDocumentRequest,
    CreateDocumentResponse,
    EmbeddedSignLinkResponse
)

# 로거 설정
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

async def get_documents(request: DocumentListRequest, offset: int, limit: int, db: Session) -> Tuple[List[dict], int]:
    url = f"{settings.MODUSIGN_BASE_URL}/documents"
    params = {
        "page": request.page,
        "per_page": limit,
        "local_kw": "ko"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=settings.MODUSIGN_HEADERS) as response:
                if response.status != 200:
                    error_data = await response.json()
                    logger.error(f"Modusign API error: {error_data}")
                    raise HTTPException(status_code=response.status, detail=error_data.get('message', 'Error'))
                data = await response.json()
                return data.get('documents', []), data.get('total_count', 0)
    except Exception as e:
        logger.error(f"Error in get_documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def create_document_with_template(request: CreateDocumentRequest, db: Session) -> CreateDocumentResponse:
    url = f"{settings.MODUSIGN_BASE_URL}/documents/request-with-template?local_kw=ko"
    payload = {
        "templateId": request.templateId,
        "document": request.document.dict()
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=settings.MODUSIGN_HEADERS) as response:
            if response.status != 200:
                error_data = await response.json()
                logger.error(f"Modusign API error: {error_data}")
                raise HTTPException(status_code=response.status, detail=error_data.get('message', 'Error'))
            data = await response.json()
    return CreateDocumentResponse(**data)

async def request_document_signature(document_id: str, db: Session) -> EmbeddedSignLinkResponse:
    url = f"{settings.MODUSIGN_BASE_URL}/documents/{document_id}/embedded-view?local_kw=ko"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=settings.MODUSIGN_HEADERS) as response:
            if response.status != 200:
                error_data = await response.json()
                logger.error(f"Modusign API error: {error_data}")
                raise HTTPException(status_code=response.status, detail=error_data.get('message', 'Error'))
            data = await response.json()
    return EmbeddedSignLinkResponse(embeddedUrl=data['embeddedUrl'])

async def delete_document(document_id: str, db: Session) -> bool:
    url = f"{settings.MODUSIGN_BASE_URL}/documents/{document_id}?local_kw=ko"
    async with aiohttp.ClientSession() as session:
        async with session.delete(url, headers=settings.MODUSIGN_HEADERS) as response:
            if response.status != 204:
                error_data = await response.json()
                logger.error(f"Modusign API error: {error_data}")
                raise HTTPException(status_code=response.status, detail=error_data.get('message', 'Error'))
            return True

async def get_document_details(document_id: str, db: Session) -> Dict[str, Any]:
    url = f"{settings.MODUSIGN_BASE_URL}/documents/{document_id}?local_kw=ko"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=settings.MODUSIGN_HEADERS) as response:
            if response.status != 200:
                error_data = await response.json()
                logger.error(f"Modusign API error: {error_data}")
                raise HTTPException(status_code=response.status, detail=error_data.get('message', 'Error'))
            return await response.json()