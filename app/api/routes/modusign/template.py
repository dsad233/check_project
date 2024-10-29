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
                "extension": "pdf"
            },
            "participants": [
                {
                    "role": "근로자",
                    "signingOrder": 1,
                    "signingMethod": {
                        "type": "EMAIL",
                        "value": "employee@workswave.com"
                    }
                }
            ],
            "fieldPositions": [
                {
                    "type": "SIGN",
                    "role": "근로자",
                    "x": 100,
                    "y": 200,
                    "width": 120,
                    "height": 50,
                    "pageNumber": 1,
                    "required": True
                }
            ]
        }
        
        # 요청 데이터 로깅
        logger.info("=== Template Creation Request ===")
        logger.info(f"Request Data: {json.dumps(template_data, indent=2, ensure_ascii=False)}")
        
        response = await template_service.create_template(template_data)
        
        # 응답 데이터 로깅
        logger.info("=== Template Creation Response ===")
        logger.info(f"Response Data: {json.dumps(response.dict(), indent=2, ensure_ascii=False)}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in create_test_template: {str(e)}")
        logger.error(f"Template data: {json.dumps(template_data, indent=2, ensure_ascii=False)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create", response_model=TemplateResponse)
async def create_template(
    title: str = Form(...),
    file: UploadFile = File(...),
    participants: str = Form(...),
    elements: Optional[str] = Form(None)
):
    try:
        template_data = {
            "title": title,
            "file": {
                "name": file.filename,
                "base64": base64.b64encode(await file.read()).decode('utf-8'),
                "extension": "pdf"
            },
            "participants": json.loads(participants)
        }
        
        if elements:
            try:
                elements_data = json.loads(elements)
                field_positions = []
                
                for element in elements_data:
                    field = {
                        "type": element.get("type", "SIGN"),
                        "role": element["role"],
                        "x": int(element["x"]),
                        "y": int(element["y"]),
                        "width": int(element["width"]),
                        "height": int(element["height"]),
                        "pageNumber": int(element.get("pageNumber", 1)),
                        "required": bool(element.get("required", True))
                    }
                    
                    # TEXT 타입인 경우 placeholder 추가
                    if element.get("type") == "TEXT" and "placeholder" in element:
                        field["placeholder"] = element["placeholder"]
                        
                    field_positions.append(field)
                
                template_data["fieldPositions"] = field_positions
                logger.info(f"Added fieldPositions: {template_data['fieldPositions']}")
                
            except Exception as e:
                logger.error(f"Error processing elements data: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Invalid elements format: {str(e)}")
        
        try:
            response = await template_service.create_template(template_data)
            logger.info(f"Template created successfully: {response}")
            return response
        except Exception as e:
            logger.error(f"Error from API: {str(e)}")
            raise
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
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
