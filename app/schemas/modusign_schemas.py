from typing import List, Optional

from pydantic import BaseModel


class DeleteSignCancelPayload(BaseModel):
    accessibleByParticipant: bool
    message: str


class SigningMethod(BaseModel):
    type: str
    value: str


class ParticipantMapping(BaseModel):
    excluded: bool
    signingMethod: SigningMethod
    signingDuration: int
    role: str
    name: str
    locale: str


class RequesterInputMapping(BaseModel):
    key: str
    value: str


class PayloadMetadata(BaseModel):
    key: str
    value: str


class CreateCustomerConsentFormPayload(BaseModel):
    class CreateCustomerConsentForm(BaseModel):
        participantMappings: List[ParticipantMapping]
        requesterInputMappings: Optional[List[RequesterInputMapping]] = []
        title: str
        metadatas: List[PayloadMetadata]

    document: CreateCustomerConsentForm
    templateId: str


class CreateCustomerConsentFormResponse(BaseModel):
    document_id: str | None = None
    participant_id: str | None = None
    embedded_url: str | None = None


class CreateConsentFormPayload(BaseModel):
    class CreateConsentFormDocument(BaseModel):
        participantMappings: List[ParticipantMapping]
        requesterInputMappings: Optional[List[RequesterInputMapping]] = []
        title: str
        metadatas: List[PayloadMetadata]

    document: CreateConsentFormDocument
    templateId: str


class EmbeddedSignLinkResponse(BaseModel):
    document_id: str | None = None
    participant_id: str | None = None
    embedded_url: str | None = None


class CreateTreatmentFormResponse(BaseModel):
    document_id: str | None = None
    participant_id: str | None = None
