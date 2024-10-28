import requests
from sqlalchemy.orm import Session
from typing import List, Tuple, Dict, Any
from app.core.modusign_config import MODUSIGN_BASE_URL, MODUSIGN_HEADERS
from app.schemas.modusign_schemas import EmbeddedSignLinkResponse, CreateDocumentResponse, CreateCustomerConsentFormPayload
from app.schemas.sign_schemas import DocumentListRequest

async def get_documents(request: DocumentListRequest, offset: int, limit: int, db: Session) -> Tuple[List[dict], int]:
    url = f"{MODUSIGN_BASE_URL}/documents?page={request.page}&limit={limit}"
    response = requests.get(url, headers=MODUSIGN_HEADERS)
    response.raise_for_status()
    data = response.json()
    return data['data'], data['total']

async def create_document_with_template(request: CreateCustomerConsentFormPayload, db: Session) -> CreateDocumentResponse:
    url = f"{MODUSIGN_BASE_URL}/documents/request-with-template"
    payload = request.dict()
    response = requests.post(url, json=payload, headers=MODUSIGN_HEADERS)
    response.raise_for_status()
    return CreateDocumentResponse(**response.json())

async def request_document_signature(document_id: str, db: Session) -> EmbeddedSignLinkResponse:
    url = f"{MODUSIGN_BASE_URL}/documents/{document_id}/embedded-view"
    response = requests.get(url, headers=MODUSIGN_HEADERS)
    response.raise_for_status()
    data = response.json()
    return EmbeddedSignLinkResponse(embedded_url=data['embeddedUrl'])

async def delete_document(document_id: str, db: Session) -> bool:
    url = f"{MODUSIGN_BASE_URL}/documents/{document_id}"
    response = requests.delete(url, headers=MODUSIGN_HEADERS)
    return response.status_code == 204

async def get_document_details(document_id: str, db: Session) -> Dict[str, Any]:
    url = f"{MODUSIGN_BASE_URL}/documents/{document_id}"
    response = requests.get(url, headers=MODUSIGN_HEADERS)
    response.raise_for_status()
    return response.json()

async def cancel_document_request(document_id: str, db: Session) -> Dict[str, Any]:
    url = f"{MODUSIGN_BASE_URL}/documents/{document_id}/cancel"
    response = requests.post(url, headers=MODUSIGN_HEADERS)
    response.raise_for_status()
    return response.json()

async def request_document_correction(document_id: str, participant_id: str, message: str, db: Session) -> Dict[str, Any]:
    url = f"{MODUSIGN_BASE_URL}/documents/{document_id}/request-correction"
    payload = {"participantId": participant_id, "message": message}
    response = requests.post(url, json=payload, headers=MODUSIGN_HEADERS)
    response.raise_for_status()
    return response.json()

async def resend_notification(document_id: str, participant_id: str, db: Session) -> Dict[str, Any]:
    url = f"{MODUSIGN_BASE_URL}/documents/{document_id}/resend-notification"
    payload = {"participantId": participant_id}
    response = requests.post(url, json=payload, headers=MODUSIGN_HEADERS)
    response.raise_for_status()
    return response.json()

async def update_signing_deadline(document_id: str, signing_due: Dict[str, Any], db: Session) -> Dict[str, Any]:
    url = f"{MODUSIGN_BASE_URL}/documents/{document_id}/signing-due"
    response = requests.put(url, json=signing_due, headers=MODUSIGN_HEADERS)
    response.raise_for_status()
    return response.json()

async def update_document_metadata(document_id: str, metadatas: List[Dict[str, str]], db: Session) -> Dict[str, Any]:
    url = f"{MODUSIGN_BASE_URL}/documents/{document_id}/metadatas"
    payload = {"metadatas": metadatas}
    response = requests.put(url, json=payload, headers=MODUSIGN_HEADERS)
    response.raise_for_status()
    return response.json()

async def get_document_history(document_id: str, db: Session) -> Dict[str, Any]:
    url = f"{MODUSIGN_BASE_URL}/documents/{document_id}/history"
    response = requests.get(url, headers=MODUSIGN_HEADERS)
    response.raise_for_status()
    return response.json()

async def update_document_status(document_id: str, status: str, db: Session) -> Dict[str, Any]:
    # 실제로는 DB 업데이트 로직이 필요합니다. 여기서는 모두싸인 API를 호출하여 상태를 업데이트합니다.
    url = f"{MODUSIGN_BASE_URL}/documents/{document_id}"
    payload = {"status": status}
    response = requests.put(url, json=payload, headers=MODUSIGN_HEADERS)
    response.raise_for_status()
    return response.json()

async def get_participant_fields(document_id: str, db: Session) -> Dict[str, Any]:
    url = f"{MODUSIGN_BASE_URL}/documents/{document_id}/participant-fields"
    response = requests.get(url, headers=MODUSIGN_HEADERS)
    response.raise_for_status()
    return response.json()

async def get_requester_inputs(document_id: str, db: Session) -> Dict[str, Any]:
    url = f"{MODUSIGN_BASE_URL}/documents/{document_id}/requester-inputs"
    response = requests.get(url, headers=MODUSIGN_HEADERS)
    response.raise_for_status()
    return response.json()

async def forward_document_bundle(document_id: str, email: str, db: Session) -> Dict[str, Any]:
    url = f"{MODUSIGN_BASE_URL}/documents/{document_id}/forward"
    payload = {"email": email}
    response = requests.post(url, json=payload, headers=MODUSIGN_HEADERS)
    response.raise_for_status()
    return response.json()