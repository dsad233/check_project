import logging
import requests
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.schemas.sign_schemas import CreateSignWebhookRequest
from app.core.modusign_config import MODUSIGN_BASE_URL, MODUSIGN_HEADERS

logger = logging.getLogger(__name__)

async def process_webhook(request: CreateSignWebhookRequest, db: Session) -> None:
    document_id = request.document.id
    event_type = request.event.type
    
    try:
        document_details = await get_document_details(document_id)
        
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

async def get_document_details(document_id: str) -> Dict[str, Any]:
    url = f"{MODUSIGN_BASE_URL}/documents/{document_id}"
    response = requests.get(url, headers=MODUSIGN_HEADERS)
    response.raise_for_status()
    return response.json()

async def update_document_status(document_id: str, status: str, db: Session) -> None:
    # 내부 데이터베이스 상태 업데이트 로직 구현
    # 예: db.query(Document).filter(Document.id == document_id).update({"status": status})
    # db.commit()
    pass

async def handle_document_started(document_details: Dict[str, Any], db: Session) -> None:
    logger.info(f"Document started: {document_details['id']}")
    await update_document_status(document_details['id'], 'STARTED', db)

async def handle_document_signed(document_details: Dict[str, Any], db: Session) -> None:
    logger.info(f"Document signed: {document_details['id']}")
    await update_document_status(document_details['id'], 'SIGNED', db)
    await remind_next_signer(document_details['id'])

async def handle_document_all_signed(document_details: Dict[str, Any], db: Session) -> None:
    logger.info(f"Document all signed: {document_details['id']}")
    await update_document_status(document_details['id'], 'COMPLETED', db)

async def handle_document_rejected(document_details: Dict[str, Any], db: Session) -> None:
    logger.info(f"Document rejected: {document_details['id']}")
    await update_document_status(document_details['id'], 'REJECTED', db)

async def handle_document_request_canceled(document_details: Dict[str, Any], db: Session) -> None:
    logger.info(f"Document request canceled: {document_details['id']}")
    await update_document_status(document_details['id'], 'CANCELED', db)

async def handle_document_signing_canceled(document_details: Dict[str, Any], db: Session) -> None:
    logger.info(f"Document signing canceled: {document_details['id']}")
    await update_document_status(document_details['id'], 'SIGNING_CANCELED', db)
    await request_correction(document_details['id'])

async def remind_next_signer(document_id: str) -> None:
    url = f"{MODUSIGN_BASE_URL}/documents/{document_id}/remind-signing"
    response = requests.post(url, headers=MODUSIGN_HEADERS)
    response.raise_for_status()

async def request_correction(document_id: str) -> None:
    url = f"{MODUSIGN_BASE_URL}/documents/{document_id}/request-correction"
    payload = {
        "participantId": "PARTICIPANT_ID",  # 실제 참여자 ID로 대체해야 함
        "message": "서명 내용을 수정해 주세요."
    }
    response = requests.post(url, json=payload, headers=MODUSIGN_HEADERS)
    response.raise_for_status()