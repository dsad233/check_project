from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body, Form
import logging
import base64
import json
from app.middleware.tokenVerify import validate_token
from app.schemas.modusign_schemas import (
    TemplateResponse,
    TemplateListResponse,
    TemplateElement,
    RequesterInput
)
from app.service.template_service import TemplateService
from reportlab.pdfgen import canvas
import io
from typing import List, Optional

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/templates", dependencies=[Depends(validate_token)])
template_service = TemplateService()

@router.post("/test", response_model=TemplateResponse)
async def create_test_template():
    """테스트용 템플릿 생성"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 750, "샘플 근로계약서")
    c.save()
    
    pdf_content = buffer.getvalue()
    base64_content = base64.b64encode(pdf_content).decode('utf-8')
    
    try:
        template_data = {
            "title": "[테스트] 표준 근로계약서",
            "file": {
                "name": "test_contract.pdf",
                "base64": base64_content,
                "extension": "pdf",
                "contentType": "application/pdf"
            },
            "participants": [
                {
                    "role": "근로자",
                    "signingOrder": 1
                }
            ],
            "elements": [
                {
                    "type": "SIGN",
                    "role": "근로자",
                    "x": 100,
                    "y": 200,
                    "width": 120,
                    "height": 50,
                    "page": 1
                }
            ]
        }
        
        logger.info(f"Creating template with data: {template_data}")
        return await template_service.create_template(template_data)
    except Exception as e:
        logger.error(f"Error in create_test_template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create", response_model=TemplateResponse)
async def create_template(
    title: str = Form(..., description="템플릿 제목"),
    file: UploadFile = File(..., description="PDF 파일"),
    participants: str = Form(..., description="""참여자 정보 목록 (JSON string)
    예시:
    [
        {
            "role": "근로자",
            "signingOrder": 1,
            "signingMethod": {
                "type": "EMAIL",
                "value": "employee@example.com"
            }
        }
    ]""")
):
    """템플릿 생성 API"""
    try:
        # JSON string을 파싱
        participants_data = json.loads(participants)
        
        # 파일 내용 읽기
        file_content = await file.read()
        base64_content = base64.b64encode(file_content).decode('utf-8')
        
        # API 요청 데이터 구성
        template_data = {
            "title": title,
            "file": {
                "name": file.filename,
                "base64": base64_content,
                "extension": "pdf"
            },
            "participants": [
                {
                    "role": participant["role"],
                    "signingOrder": participant.get("signingOrder", 1),
                    "signingMethod": {
                        "type": "EMAIL",
                        "value": participant["signingMethod"]["value"]
                    }
                } for participant in participants_data
            ]
        }
        
        logger.info(f"Creating template with data: {json.dumps(template_data, indent=2)}")
        return await template_service.create_template(template_data)
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid participants format: {str(e)}")
    except KeyError as e:
        logger.error(f"Missing required field: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Missing required field: {str(e)}")
    except Exception as e:
        logger.error(f"Error in create_template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=TemplateListResponse)
async def get_templates():
    """템플릿 목록 조회"""
    try:
        return await template_service.get_templates()
    except Exception as e:
        logger.error(f"Error in get_templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: str):
    """템플릿 상세 정보 조회"""
    try:
        return await template_service.get_template(template_id)
    except Exception as e:
        logger.error(f"Error in get_template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{template_id}")
async def delete_template(template_id: str):
    """템플릿 삭제"""
    try:
        success = await template_service.delete_template(template_id)
        if not success:
            raise HTTPException(status_code=404, detail="Template not found")
        return {"message": "Template deleted successfully"}
    except Exception as e:
        logger.error(f"Error in delete_template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
