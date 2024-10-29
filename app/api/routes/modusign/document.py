from fastapi import APIRouter, Depends, HTTPException
from app.middleware.tokenVerify import validate_token
from app.schemas.modusign_schemas import (
    DocumentListRequest, 
    DocumentListResponse,
    CreateDocumentRequest,
    CreateDocumentResponse,
    EmbeddedSignLinkResponse
)
from app.service.document_service import DocumentService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", dependencies=[Depends(validate_token)])
document_service = DocumentService()

@router.get("", response_model=DocumentListResponse)
async def get_documents():
    """문서 목록 조회"""
    try:
        response = await document_service.get_documents()
        
        # API 응답을 스키마에 맞게 변환
        return DocumentListResponse(
            documents=response.get('data', []), 
            total_count=response.get('total_count', 0)
        )
    except Exception as e:
        logger.error(f"Error in get_documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=CreateDocumentResponse)
async def create_document(request: CreateDocumentRequest):
    """템플릿으로부터 실제 문서 생성"""
    try:
        document_data = {
            "templateId": request.templateId,
            "document": {
                "title": "홍길동님의 근로계약서",
                "participantMappings": [
                    {
                        "role": "근로자",
                        "name": "홍길동",
                        "signingMethod": {
                            "type": "EMAIL",
                            "value": "employee@example.com"
                        }
                    },
                    {
                        "role": "고용주",
                        "name": "김사장",
                        "signingMethod": {
                            "type": "EMAIL",
                            "value": "employer@workswave.com"
                        }
                    }
                ],
                "requesterInputMappings": [
                    {
                        "key": "employee_name",
                        "value": "홍길동",
                        "dataLabel": "근로자 성명"
                    },
                    {
                        "key": "employee_email",
                        "value": "employee@example.com",
                        "dataLabel": "근로자 이메일"
                    },
                    {
                        "key": "start_date",
                        "value": "2024-01-01",
                        "dataLabel": "근로 개시일"
                    },
                    {
                        "key": "salary",
                        "value": "3,000,000",
                        "dataLabel": "월 급여"
                    }
                ]
            }
        }
        
        return await document_service.create_document(document_data)
    except Exception as e:
        logger.error(f"Error in create_document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/{document_id}/sign", response_model=EmbeddedSignLinkResponse)
async def request_document_signature(
    document_id: str,
):
    try:
        return await document_service.request_document_signature(document_id=document_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
):
    try:
        success = await document_service.delete_document(document_id=document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}")
async def get_document_details(
    document_id: str,
):
    try:
        return await document_service.get_document_details(document_id=document_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
