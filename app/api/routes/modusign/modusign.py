from fastapi import APIRouter, Depends, HTTPException
import logging
from app.middleware.tokenVerify import validate_token
from app.schemas.modusign_schemas import (
    DocumentListRequest, 
    DocumentListResponse,
    CreateDocumentRequest,
    CreateDocumentResponse,
    EmbeddedSignLinkResponse
)
from app.service.document_service import DocumentService

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(dependencies=[Depends(validate_token)])
document_service = DocumentService()

@router.get("/documents", response_model=DocumentListResponse)
async def get_documents(
    query: DocumentListRequest = Depends(),
):
    logger.info("Starting get_documents endpoint")
    try:
        logger.info(f"Query parameters: page={query.page}, per_page={query.per_page}")
        documents, total_count = await document_service.get_documents(
            request=query, 
            offset=(query.page - 1) * query.per_page,
            limit=query.per_page
        )
        logger.info(f"Successfully retrieved {len(documents)} documents")
        return DocumentListResponse(data=documents, total_count=total_count)
    except Exception as e:
        logger.error(f"Error in get_documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents", response_model=CreateDocumentResponse)
async def create_document(
    request: CreateDocumentRequest,
):
    logger.info("Starting create_document endpoint")
    try:
        return await document_service.create_document_with_template(request=request)
    except Exception as e:
        logger.error(f"Error in create_document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/{document_id}/sign", response_model=EmbeddedSignLinkResponse)
async def request_document_signature(
    document_id: str,
):
    logger.info(f"Starting request_document_signature endpoint for document {document_id}")
    try:
        return await document_service.request_document_signature(document_id=document_id)
    except Exception as e:
        logger.error(f"Error in request_document_signature: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
):
    logger.info(f"Starting delete_document endpoint for document {document_id}")
    try:
        success = await document_service.delete_document(document_id=document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        logger.info(f"Successfully deleted document {document_id}")
        return {"message": "Document deleted successfully"}
    except Exception as e:
        logger.error(f"Error in delete_document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}")
async def get_document_details(
    document_id: str,
):
    logger.info(f"Starting get_document_details endpoint for document {document_id}")
    try:
        return await document_service.get_document_details(document_id=document_id)
    except Exception as e:
        logger.error(f"Error in get_document_details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))