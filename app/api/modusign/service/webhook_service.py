from sqlalchemy.orm import Session
from typing import Dict, Any
import logging
from app.schemas.sign_schemas import CreateSignWebhookRequest
from .document_service import get_document_details

logger = logging.getLogger(__name__)

async def process_webhook(request: CreateSignWebhookRequest, db: Session) -> None:
    document_id = request.document.id
    event_type = request.event.type
    
    try:
        document_details = await get_document_details(document_id, db)
        
        event_handlers = {
            "document_started": handle_document_started,
            "document_signed": handle_document_signed,
            "document_all_signed": handle_document_all_signed,
            "document_rejected": handle_document_rejected,
            "document_request_canceled": handle_document_request_canceled,
            "document_signing_canceled": handle_document_signing_canceled
        }
        
        handler = event_handlers.get(event_type)
        if handler:
            await handler(document_details, db)
        else:
            logger.warning(f"Unhandled webhook event type: {event_type}")
    
    except Exception as e:
        logger.error(f"Error processing webhook for document {document_id}: {str(e)}")
        # 에러 처리 로직 추가 (예: 알림 발송, 에러 로깅 등)

async def handle_document_started(document_details: Dict[str, Any], db: Session) -> None:
    logger.info(f"Document started: {document_details['id']}")
    # TODO: 문서 상태 업데이트, 관련 비즈니스 로직 처리

async def handle_document_signed(document_details: Dict[str, Any], db: Session) -> None:
    logger.info(f"Document signed: {document_details['id']}")
    # TODO: 서명 상태 업데이트, 다음 서명자 알림 등

async def handle_document_all_signed(document_details: Dict[str, Any], db: Session) -> None:
    logger.info(f"Document all signed: {document_details['id']}")
    # TODO: 문서 상태 완료로 업데이트, 관련 비즈니스 로직 처리 (예: 계약 체결 완료 처리)

async def handle_document_rejected(document_details: Dict[str, Any], db: Session) -> None:
    logger.info(f"Document rejected: {document_details['id']}")
    # TODO: 문서 상태 업데이트, 요청자에게 알림 등

async def handle_document_request_canceled(document_details: Dict[str, Any], db: Session) -> None:
    logger.info(f"Document request canceled: {document_details['id']}")
    # TODO: 문서 상태 업데이트, 관련 비즈니스 로직 처리

async def handle_document_signing_canceled(document_details: Dict[str, Any], db: Session) -> None:
    logger.info(f"Document signing canceled: {document_details['id']}")
    # TODO: 문서 상태 업데이트, 요청자에게 알림 등