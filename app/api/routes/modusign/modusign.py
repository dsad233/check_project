from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import async_session
from app.middleware.tokenVerify import validate_token
from app.schemas.modusign_schemas import EmbeddedSignLinkResponse, CreateDocumentResponse, CreateCustomerConsentFormPayload
from app.schemas.sign_schemas import (
    DocumentListRequest,
    DocumentListResponse,
    CreateSignWebhookRequest
)
from app.api.service import webhook_service
from app.api.service import document_service

router = APIRouter(dependencies=[Depends(validate_token)])
db = async_session()

@router.get("/documents", summary="문서 목록 조회", response_model=DocumentListResponse)
async def get_documents(
    request: DocumentListRequest = Depends(),
    db: Session = Depends(async_session),
):
    offset = (request.page - 1) * request.per_page
    limit = request.per_page

    documents, total_count = await document_service.get_documents(
        request=request, offset=offset, limit=limit, db=db
    )

    return DocumentListResponse(
        data=[DocumentListResponse.Document(**doc) for doc in documents],
        total_count=total_count,
    )

@router.post("/documents", summary="템플릿으로 새 문서 생성 및 서명 요청", response_model=CreateDocumentResponse)
async def create_document(
    request: CreateCustomerConsentFormPayload,
    db: Session = Depends(async_session),
):
    return await document_service.create_document_with_template(request=request, db=db)

@router.post("/documents/{document_id}/sign", summary="문서 서명 요청", response_model=EmbeddedSignLinkResponse)
async def request_document_signature(
    document_id: str,
    db: Session = Depends(async_session),
):
    return await document_service.request_document_signature(document_id=document_id, db=db)

@router.delete("/documents/{document_id}", summary="문서 삭제")
async def delete_document(
    document_id: str,
    db: Session = Depends(async_session),
):
    success = await document_service.delete_document(document_id=document_id, db=db)
    if success:
        return {"message": "Document deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Document not found")

@router.get("/documents/{document_id}", summary="문서 상세 조회")
async def get_document_details(
    document_id: str,
    db: Session = Depends(async_session),
):
    return await document_service.get_document_details(document_id=document_id, db=db)

@router.post("/webhook", summary="모두싸인 웹훅 처리")
async def sign_webhook(
    request: CreateSignWebhookRequest,
    db: Session = Depends(async_session),
):
    await webhook_service.process_webhook(request=request, db=db)
    return {"message": "Webhook processed successfully"}