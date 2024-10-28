import aiohttp
import logging
import json
import base64
import traceback
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
        logger.info(f"ModuSign headers initialized: {self.headers}")

    async def get_documents(self, request: DocumentListRequest, offset: int, limit: int, db: Session) -> Tuple[List[dict], int]:
        url = f"{MODUSIGN_BASE_URL}/documents"
        
        logger.info(f"Requesting documents from: {url}")
        logger.info(f"Headers: {self.headers}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    response_text = await response.text()
                    logger.info(f"Response status: {response.status}")
                    logger.info(f"Response text: {response_text}")
                    
                    if response.status != 200:
                        logger.error(f"Error response from ModuSign: {response_text}")
                        try:
                            error_data = json.loads(response_text)
                            detail = error_data.get('message', 'Error getting documents')
                        except json.JSONDecodeError:
                            detail = response_text
                        raise HTTPException(
                            status_code=response.status,
                            detail=detail
                        )
                    
                    try:
                        data = json.loads(response_text)
                        documents = data.get('documents', [])
                        total_count = data.get('total_count', 0)
                        logger.info(f"Successfully retrieved {len(documents)} documents")
                        return documents, total_count
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse response JSON: {e}")
                        raise HTTPException(
                            status_code=500,
                            detail="Invalid JSON response from ModuSign API"
                        )
                        
        except aiohttp.ClientError as e:
            logger.error(f"HTTP request failed: {e}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail=f"Failed to connect to ModuSign API: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error in get_documents: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )

    async def create_document_with_template(self, request: CreateDocumentRequest, db: Session) -> CreateDocumentResponse:
        url = f"{MODUSIGN_BASE_URL}/documents/request-with-template"
        payload = {
            "templateId": request.templateId,
            "document": request.document.dict()
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=self.headers) as response:
                    response_text = await response.text()
                    if response.status != 200:
                        error_data = json.loads(response_text)
                        raise HTTPException(
                            status_code=response.status,
                            detail=error_data.get('message', 'Error creating document')
                        )
                    data = json.loads(response_text)
                    return CreateDocumentResponse(
                        document_id=data.get('id'),
                        participant_id=data.get('participants', [{}])[0].get('id') if data.get('participants') else None,
                        embedded_url=None
                    )
        except Exception as e:
            logger.error(f"Error in create_document_with_template: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def request_document_signature(self, document_id: str, db: Session) -> EmbeddedSignLinkResponse:
        url = f"{MODUSIGN_BASE_URL}/documents/{document_id}/embedded-view"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    response_text = await response.text()
                    if response.status != 200:
                        error_data = json.loads(response_text)
                        raise HTTPException(
                            status_code=response.status,
                            detail=error_data.get('message', 'Error getting signature link')
                        )
                    data = json.loads(response_text)
                    return EmbeddedSignLinkResponse(embeddedUrl=data['embeddedUrl'])
        except Exception as e:
            logger.error(f"Error in request_document_signature: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_document(self, document_id: str, db: Session) -> bool:
        url = f"{MODUSIGN_BASE_URL}/documents/{document_id}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(url, headers=self.headers) as response:
                    return response.status == 204
        except Exception as e:
            logger.error(f"Error in delete_document: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_document_details(self, document_id: str, db: Session) -> Dict[str, Any]:
        url = f"{MODUSIGN_BASE_URL}/documents/{document_id}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    response_text = await response.text()
                    if response.status != 200:
                        error_data = json.loads(response_text)
                        raise HTTPException(
                            status_code=response.status,
                            detail=error_data.get('message', 'Error getting document details')
                        )
                    return json.loads(response_text)
        except Exception as e:
            logger.error(f"Error in get_document_details: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))