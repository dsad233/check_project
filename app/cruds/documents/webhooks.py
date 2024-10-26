from app.core.config import MODUSIGN_BASE_URL, MODUSIGN_HEADERS, MODUSIGN_WEBHOOK_URL
import requests
from typing import Dict, Any, List

def create_webhook(name: str, events: List[str], headers: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """새 웹훅을 생성합니다."""
    url = f"{MODUSIGN_BASE_URL}/webhooks"
    payload = {
        "name": name,
        "url": MODUSIGN_WEBHOOK_URL,
        "events": events
    }
    if headers:
        payload["headers"] = headers
    response = requests.post(url, json=payload, headers=MODUSIGN_HEADERS)
    response.raise_for_status()
    return response.json()

def get_webhook(webhook_id: str) -> Dict[str, Any]:
    """특정 ID의 웹훅 정보를 조회합니다."""
    url = f"{MODUSIGN_BASE_URL}/webhooks/{webhook_id}"
    response = requests.get(url, headers=MODUSIGN_HEADERS)
    response.raise_for_status()
    return response.json()

def update_webhook(webhook_id: str, name: str = None, events: List[str] = None, headers: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """웹훅을 업데이트합니다."""
    url = f"{MODUSIGN_BASE_URL}/webhooks/{webhook_id}"
    payload = {}
    if name:
        payload["name"] = name
    if events:
        payload["events"] = events
    if headers:
        payload["headers"] = headers
    response = requests.put(url, json=payload, headers=MODUSIGN_HEADERS)
    response.raise_for_status()
    return response.json()

def delete_webhook(webhook_id: str) -> bool:
    """웹훅을 삭제합니다."""
    url = f"{MODUSIGN_BASE_URL}/webhooks/{webhook_id}"
    response = requests.delete(url, headers=MODUSIGN_HEADERS)
    response.raise_for_status()
    return response.status_code == 204

def list_webhooks(page: int = 1, limit: int = 10) -> Dict[str, Any]:
    """웹훅 목록을 조회합니다."""
    url = f"{MODUSIGN_BASE_URL}/webhooks?page={page}&limit={limit}"
    response = requests.get(url, headers=MODUSIGN_HEADERS)
    response.raise_for_status()
    return response.json()