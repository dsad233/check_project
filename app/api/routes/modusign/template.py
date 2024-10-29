from fastapi import APIRouter, Depends, HTTPException
import logging
from app.middleware.tokenVerify import validate_token
from app.schemas.modusign_schemas import TemplateResponse, TemplateListResponse
from app.service.template_service import TemplateService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/templates", dependencies=[Depends(validate_token)])
template_service = TemplateService()

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
    logger.info(f"Received template_id: {template_id}")
    logger.info(f"Template ID type: {type(template_id)}")
    
    success = await template_service.delete_template(template_id)
    return {"message": "Template deleted successfully"}
