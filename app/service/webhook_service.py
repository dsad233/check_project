import logging
from typing import Dict
from fastapi import HTTPException
from app.core.config import settings
import aiohttp

logger = logging.getLogger(__name__)
MODUSIGN_API_URL = "https://api.modusign.co.kr"

class WebhookService:
    def __init__(self):
        self.headers = settings.MODUSIGN_HEADERS

    async def create_webhook(self, webhook_data: dict) -> Dict:
        """웹훅 생성"""
        try:
            result = await self._make_request(
                'POST',
                f"{MODUSIGN_API_URL}/webhooks",
                json={
                    "url": f"{settings.MODUSIGN_WEBHOOK_URL}/webhook/callback",
                    "events": webhook_data['events'],
                    "name": webhook_data['name'],
                    "description": webhook_data.get('description'),
                    "enabled": webhook_data.get('enabled', True)
                }
            )
            return result
        except Exception as e:
            logger.error(f"Error in create_webhook: {str(e)}")
            raise

    async def handle_webhook(self, webhook_data: dict) -> Dict:
        """웹훅 이벤트 처리"""
        try:
            event_type = webhook_data.get('event')
            logger.info(f"Received webhook event: {event_type}")
            logger.info(f"Webhook data: {webhook_data}")

            # 이벤트 타입별 처리
            if event_type == "document.completed":
                document = webhook_data.get('data', {}).get('document', {})
                logger.info(f"Document completed: {document}")
                
            elif event_type == "participant.signed":
                participant = webhook_data.get('data', {}).get('participant', {})
                logger.info(f"Participant signed: {participant}")
            
            return {"status": "success", "event": event_type}
            
        except Exception as e:
            logger.error(f"Error in handle_webhook: {str(e)}")
            raise

    async def _make_request(self, method: str, url: str, **kwargs) -> Dict:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, headers=self.headers, **kwargs) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        raise HTTPException(status_code=response.status, detail=error_text)
                    return await response.json()
        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
            raise

    async def get_webhook(self, webhook_id: str) -> Dict:
        """웹훅 상세 조회"""
        try:
            result = await self._make_request(
                'GET',
                f"{MODUSIGN_API_URL}/webhooks/{webhook_id}"
            )
            return result
        except Exception as e:
            logger.error(f"Error in get_webhook: {str(e)}")
            raise