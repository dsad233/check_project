from app.core.config import MODUSIGN_BASE_URL, MODUSIGN_HEADERS
import requests
import json
from typing import Dict, Any, List

def create_template(title: str, file_data: Dict[str, str], participants: List[Dict[str, Any]], 
                    requester_inputs: List[Dict[str, Any]] = None, metadatas: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """템플릿을 생성합니다."""
    url = f"{MODUSIGN_BASE_URL}/templates"
    payload = {
        "title": title,
        "file": file_data,
        "participants": participants
    }
    if requester_inputs:
        payload["requesterInputs"] = requester_inputs
    if metadatas:
        payload["metadatas"] = metadatas

    response = requests.post(url, json=payload, headers=MODUSIGN_HEADERS)
    response.raise_for_status()
    return response.json()

def get_template(template_id: str) -> Dict[str, Any]:
    """특정 ID의 템플릿을 조회합니다."""
    url = f"{MODUSIGN_BASE_URL}/templates/{template_id}"
    response = requests.get(url, headers=MODUSIGN_HEADERS)
    response.raise_for_status()
    return response.json()

def update_template(template_id: str, title: str = None, participants: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """템플릿을 업데이트합니다."""
    url = f"{MODUSIGN_BASE_URL}/templates/{template_id}"
    payload = {}
    if title:
        payload["title"] = title
    if participants:
        payload["participants"] = participants
    response = requests.patch(url, json=payload, headers=MODUSIGN_HEADERS)
    response.raise_for_status()
    return response.json()

def delete_template(template_id: str) -> int:
    """템플릿을 삭제합니다."""
    url = f"{MODUSIGN_BASE_URL}/templates/{template_id}"
    response = requests.delete(url, headers=MODUSIGN_HEADERS)
    response.raise_for_status()
    return response.status_code

def list_templates(page: int = 1, limit: int = 10) -> Dict[str, Any]:
    """템플릿 목록을 조회합니다."""
    url = f"{MODUSIGN_BASE_URL}/templates?page={page}&limit={limit}"
    response = requests.get(url, headers=MODUSIGN_HEADERS)
    response.raise_for_status()
    return response.json()

def create_document_with_template(template_id: str, document: Dict[str, Any]) -> Dict[str, Any]:
    """템플릿으로 새 문서를 생성합니다."""
    url = f"{MODUSIGN_BASE_URL}/documents/request-with-template"
    payload = {
        "templateId": template_id,
        "document": document
    }
    response = requests.post(url, json=payload, headers=MODUSIGN_HEADERS)
    response.raise_for_status()
    return response.json()