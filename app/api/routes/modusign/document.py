from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.middleware.tokenVerify import validate_token
from app.schemas.modusign_schemas import (
    DocumentListRequest, 
    DocumentListResponse,
    CreateDocumentRequest,
    CreateDocumentResponse,
    EmbeddedSignLinkResponse,
    CreateDocumentFormRequest
)
from app.service.document_service import DocumentService
import logging
import json
from typing import List

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

@router.get("/{document_id}")
async def get_document_details(document_id: str):
    """문서 상세 조회"""
    try:
        return await document_service.get_document_details(document_id=document_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=CreateDocumentResponse)
async def create_document(
    title: str = Form(...),
    file: UploadFile = File(...),
    participants: str = Form(...)
):
    """일반 서명 요청"""
    try:
        # participants 문자열을 파싱
        try:
            participants_data = json.loads(participants)
            logger.info(f"Received participants data: {participants_data}")
            
            # 필수 필드 검증
            if not isinstance(participants_data, dict):
                raise HTTPException(status_code=400, detail="Participants must be an object")
                
            if not all(field in participants_data for field in ["name", "signingMethod"]):
                raise HTTPException(
                    status_code=400, 
                    detail="Participant must have name, signingMethod"
                )
            
            # signingMethod 검증
            signing_method = participants_data.get('signingMethod', {})
            if not isinstance(signing_method, dict):
                raise HTTPException(status_code=400, detail="signingMethod must be an object")
                
            if not all(field in signing_method for field in ['type', 'value']):
                raise HTTPException(status_code=400, detail="signingMethod must have type and value")

        except json.JSONDecodeError:
            logger.error(f"Invalid participants JSON: {participants}")
            raise HTTPException(status_code=400, detail="Invalid participants JSON format")

        document_data = {
            "title": title,
            "file": file,
            "participants": participants_data
        }
        
        logger.info(f"Sending document data: {document_data}")
        
        response = await document_service.create_document(document_data)
        return CreateDocumentResponse(
            document_id=response.get('id'),
            participant_id=response.get('recipients', [{}])[0].get('id'),
            embedded_url=None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/request-with-template", response_model=CreateDocumentResponse)
async def create_document_with_template(request: CreateDocumentRequest):
    """템플릿으로 서명 요청"""
    try:
        # API 문서에 맞게 요청 구조 수정
        document_data = {
            "templateId": request.templateId,
            "document": {
                "title": request.document.title,
                "metadatas": [
                    {
                        "key": m.key,
                        "value": m.value
                    } for m in request.document.metadatas
                ],
                "participantMappings": [
                    {
                        "name": p.name,
                        "role": p.role,
                        "signingMethod": {
                            "type": p.signingMethod.type,
                            "value": p.signingMethod.value
                        }
                    } for p in request.document.participantMappings
                ],
                "requesterInputMappings": [
                    {
                        "key": f.key,
                        "value": f.value,
                        "dataLabel": f.dataLabel
                    } for f in request.document.requesterInputMappings
                ]
            }
        }
        
        logger.info(f"Creating document with template: {json.dumps(document_data, indent=2)}")
        response = await document_service.create_document_with_template(document_data)
        
        return CreateDocumentResponse(
            document_id=response.get('id'),
            participant_id=response.get('participants', [{}])[0].get('id') if response.get('participants') else None,
            embedded_url=None
        )
    except Exception as e:
        logger.error(f"Error in create_document_with_template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}/participant-fields")
async def get_participant_fields(document_id: str):
    """서명자 입력란 조회"""
    try:
        return await document_service.get_participant_fields(document_id=document_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))