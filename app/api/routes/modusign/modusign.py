from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import async_session
from app.middleware.tokenVerify import validate_token
from app.schemas.modusign_schemas import (
    DocumentListRequest, 
    DocumentListResponse,
    CreateDocumentRequest,
    CreateDocumentResponse,
    EmbeddedSignLinkResponse
)
from app.service.document_service import DocumentService

router = APIRouter(dependencies=[Depends(validate_token)])
document_service = DocumentService()

@router.get("/documents", response_model=DocumentListResponse)
async def get_documents(
    query: DocumentListRequest = Depends(),
    db: Session = Depends(async_session),
):
    try:
        documents, total_count = await document_service.get_documents(
            request=query, 
            offset=(query.page - 1) * query.per_page,
            limit=query.per_page, 
            db=db
        )
        return DocumentListResponse(data=documents, total_count=total_count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents", response_model=CreateDocumentResponse)
async def create_document(
    request: CreateDocumentRequest,
    db: Session = Depends(async_session),
):
    try:
        return await document_service.create_document_with_template(request=request, db=db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/{document_id}/sign", response_model=EmbeddedSignLinkResponse)
async def request_document_signature(
    document_id: str,
    db: Session = Depends(async_session),
):
    try:
        return await document_service.request_document_signature(document_id=document_id, db=db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    db: Session = Depends(async_session),
):
    try:
        success = await document_service.delete_document(document_id=document_id, db=db)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}")
async def get_document_details(
    document_id: str,
    db: Session = Depends(async_session),
):
    try:
        return await document_service.get_document_details(document_id=document_id, db=db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))