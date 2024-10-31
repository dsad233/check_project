from fastapi import APIRouter, Depends, HTTPException
from app.middleware.tokenVerify import validate_token
from app.schemas.modusign_schemas import WebhookCreate
from app.service.webhook_service import WebhookService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(dependencies=[Depends(validate_token)])
webhook_service = WebhookService()

@router.post("/webhook")
async def create_webhook(webhook_data: WebhookCreate):
    """웹훅 생성"""
    try:
        return await webhook_service.create_webhook(webhook_data.model_dump())
    except Exception as e:
        logger.error(f"Error in create_webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook/callback", dependencies=[])
async def handle_webhook(webhook_data: dict):
    """모두싸인 웹훅 콜백 처리"""
    try:
        return await webhook_service.handle_webhook(webhook_data)
    except Exception as e:
        logger.error(f"Error in handle_webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/webhook/{webhook_id}")
async def get_webhook(webhook_id: str):
    """웹훅 상세 조회"""
    try:
        return await webhook_service.get_webhook(webhook_id)
    except Exception as e:
        logger.error(f"Error in get_webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))