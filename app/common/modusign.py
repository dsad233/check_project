import json
import uuid
from datetime import UTC, datetime

import requests
from sqlalchemy.orm import Session

from feynman_api.app.admin.crud import staff_crud
from feynman_api.app.admin.crud.sign_crud import get_treatment_form_by_document_id, update_treatment_form
from feynman_api.app.crm.constants import FormTypeEnum, SignChannelEnum, SignDocumentStatusEnum
from feynman_api.app.crm.crud import customer_crud, sign_crud
from feynman_api.app.crm.models import Customer
from feynman_api.app.crm.schemas.sign_schemas import (
    CreateConsentFormRequest,
    CreateSignWebhookRequest,
)
from feynman_api.config import settings

from .modusign_schemas import (
    CreateConsentFormPayload,
    CreateCustomerConsentFormPayload,
    CreateCustomerConsentFormResponse,
    DeleteSignCancelPayload,
    EmbeddedSignLinkResponse,
    ParticipantMapping,
    PayloadMetadata,
    SigningMethod,
)
from .s3 import S3Uploader


class SignService:
    def __init__(self) -> None:
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Basic {settings.MODUSIGN_ACCESS_KEY}",
        }
        treatment_template_id = "e1b937f0-8598-11ef-89f7-29e4f8f59f91"

        self.headers = headers
        self.treatment_template_id = treatment_template_id

    # 모두싸인 고객 정보 매핑 service
    def generate_input_mappings(self, customer: Customer, extra_data_label: dict) -> list:
        requester_input_mappings = []

        for extra_data in extra_data_label:
            if extra_data["value"] == "customer_name":
                requester_input_mappings.append({"value": f"{customer.name}", "dataLabel": extra_data["dataLabel"]})
            elif extra_data["value"] == "customer_name2":
                requester_input_mappings.append({"value": f"{customer.name}", "dataLabel": extra_data["dataLabel"]})
            elif extra_data["value"] == "customer_name3":
                requester_input_mappings.append({"value": f"{customer.name}", "dataLabel": extra_data["dataLabel"]})
            elif extra_data["value"] == "customer_name4":
                requester_input_mappings.append({"value": f"{customer.name}", "dataLabel": extra_data["dataLabel"]})
            elif extra_data["value"] == "customer_birth":
                requester_input_mappings.append({"value": f"{customer.birth}", "dataLabel": extra_data["dataLabel"]})
            elif extra_data["value"] == "customer_phone":
                requester_input_mappings.append({"value": f"{customer.phone}", "dataLabel": extra_data["dataLabel"]})
            elif extra_data["value"] == "customer_email":
                requester_input_mappings.append({"value": f"{customer.email}", "dataLabel": extra_data["dataLabel"]})

        return requester_input_mappings

    # 문서 메타데이터 조회 service
    def get_sign_detail(self, document_id: str) -> list[str] | None:
        url = f"https://api.modusign.co.kr/documents/{document_id}"

        response = requests.get(url, headers=self.headers)
        data = json.loads(response.text)

        if "metadatas" in data:
            metadatas = data["metadatas"]
            values = []

            for metadata in metadatas:
                if "value" in metadata:
                    values.append(metadata["value"])

            return values

        return None

    # 모두싸인 서명 요청 취소 service
    def sign_cancel(self, document_id: str) -> None:
        DOCUMENT_URL = f"https://api.modusign.co.kr/documents/{document_id}/cancel"

        payload = DeleteSignCancelPayload(accessibleByParticipant=False, message="서명 취소")

        requests.post(DOCUMENT_URL, json=payload.model_dump(), headers=self.headers)

        return None

    # 전자서명 임베디드 서명자의 보안링크 조회 service
    def get_sign_embedded_secure_link(
        self, redirect_url: str, document_id: str | None, participant_id: str | None
    ) -> EmbeddedSignLinkResponse:
        EMBEDDED_DRAFT_URL = f"https://api.modusign.co.kr/documents/{document_id}/participants/{participant_id}/embedded-view?redirectUrl={redirect_url}"

        response = requests.get(EMBEDDED_DRAFT_URL, headers=self.headers)
        embedded_url = json.loads(response.text).get("embeddedUrl")

        return EmbeddedSignLinkResponse(document_id=document_id, participant_id=participant_id, embedded_url=embedded_url)

    # 시술 동의서 템플릿 서명 요청 service
    def create_customer_consent_form(
        self, customer_id: int, booking_id: int, request: CreateConsentFormRequest, db: Session
    ) -> CreateCustomerConsentFormResponse | None:
        DOCUMENT_URL = "https://api.modusign.co.kr/documents/request-with-template"

        customer = customer_crud.get_customer_by_id(customer_id, db)
        consent_form_type = sign_crud.get_consent_form_type(consent_form_type_id=request.consent_form_type_id, db=db)

        if consent_form_type is None:
            return None

        payload = CreateCustomerConsentFormPayload(
            document=CreateCustomerConsentFormPayload.CreateCustomerConsentForm(
                participantMappings=[
                    ParticipantMapping(
                        excluded=False,
                        signingMethod=SigningMethod(
                            type=request.sign_method_type,
                            value=request.sign_method_value,
                        ),
                        signingDuration=20160,
                        role=consent_form_type.role,
                        name=customer.name,
                        locale=consent_form_type.locale,
                    )
                ],
                requesterInputMappings=self.generate_input_mappings(customer, consent_form_type.extra_data_label)
                if consent_form_type.extra_data_label
                else [],
                title=f"{customer.birth} {customer.name} {consent_form_type.name}",
                metadatas=[
                    PayloadMetadata(key="master", value=f"{settings.MASTER}"),
                    PayloadMetadata(key="form_type", value=FormTypeEnum.CONSENT),
                ],
            ),
            templateId=consent_form_type.template_id,
        )

        response = requests.post(DOCUMENT_URL, json=payload.model_dump(), headers=self.headers)
        document_id = json.loads(response.text).get("id")
        participant_id = (
            json.loads(response.text).get("participants")[0].get("id")
            if json.loads(response.text).get("participants")
            else None
        )

        if document_id:
            sign_crud.create_privacy_consent_form(
                customer_id=customer_id,
                booking_id=booking_id,
                type_id=consent_form_type.id,
                channel=request.sign_method_type,
                document_id=document_id,
                participant_id=participant_id,
                db=db,
            )
        else:
            raise ValueError(json.loads(response.text).get("title"))

        return CreateCustomerConsentFormResponse(
            document_id=document_id, participant_id=participant_id, embedded_url=None
        )

    # 고객 개인정보 동의서 요청 service
    def create_privacy_consent_form(
        self, customer_id: int, booking_id: int, db: Session
    ) -> CreateCustomerConsentFormResponse | None:
        DOCUMENT_URL = "https://api.modusign.co.kr/documents/request-with-template"

        customer = customer_crud.get_customer_by_id(customer_id, db)

        consent_form_type = sign_crud.get_consent_form_by_nation(nation=customer.nation, db=db)

        if consent_form_type is None:
            return None

        payload = CreateConsentFormPayload(
            document=CreateConsentFormPayload.CreateConsentFormDocument(
                participantMappings=[
                    ParticipantMapping(
                        excluded=False,
                        signingMethod=SigningMethod(
                            type=SignChannelEnum.KAKAO if customer.phone else SignChannelEnum.EMAIL,
                            value=customer.phone if customer.phone else customer.email or "",
                        ),
                        signingDuration=20160,
                        role=consent_form_type.role,
                        name=customer.name,
                        locale=consent_form_type.locale,
                    )
                ],
                requesterInputMappings=self.generate_input_mappings(customer, consent_form_type.extra_data_label)
                if consent_form_type.extra_data_label
                else [],
                title=f"{customer.birth} {customer.name} {consent_form_type.name}",
                metadatas=[
                    PayloadMetadata(key="master", value=f"{settings.MASTER}"),
                    PayloadMetadata(key="form_type", value=FormTypeEnum.CONSENT),
                ],
            ),
            templateId=consent_form_type.template_id,
        )

        response = requests.post(DOCUMENT_URL, json=payload.model_dump(), headers=self.headers)
        document_id = json.loads(response.text).get("id")
        participant_id = (
            json.loads(response.text).get("participants")[0].get("id")
            if json.loads(response.text).get("participants")
            else None
        )

        if document_id:
            sign_crud.create_privacy_consent_form(
                customer_id=customer_id,
                booking_id=booking_id,
                type_id=consent_form_type.id,
                channel=SignChannelEnum.KAKAO if customer.phone else SignChannelEnum.EMAIL,
                document_id=document_id,
                participant_id=participant_id,
                db=db,
            )

        return CreateCustomerConsentFormResponse(
            document_id=document_id, participant_id=participant_id, embedded_url=None
        )

    # 의사용 시술 전자서명 템플릿 서명 요청 service
    def create_treatment_forms(self, treatment_ids: list[int], staff_id: int, db: Session) -> EmbeddedSignLinkResponse:
        DOCUMENT_URL = "https://api.modusign.co.kr/documents/request-with-template"

        staff = staff_crud.get_staff_by_id(staff_id, db)

        payload = CreateCustomerConsentFormPayload(
            document=CreateCustomerConsentFormPayload.CreateCustomerConsentForm(
                participantMappings=[
                    ParticipantMapping(
                        excluded=False,
                        signingMethod=SigningMethod(
                            type=SignChannelEnum.SECURE_LINK,
                            value="daehyun@mement.ai",
                        ),
                        signingDuration=20160,
                        role="Customer",
                        name=staff.name,
                        locale="ko",
                    )
                ],
                title=f"{staff.birth} {staff.name} treatment sign",
                metadatas=[
                    PayloadMetadata(key="master", value=f"{settings.MASTER}"),
                    PayloadMetadata(key="form_type", value=FormTypeEnum.TREATMENT),
                ],
            ),
            templateId=self.treatment_template_id,
        )

        response = requests.post(DOCUMENT_URL, json=payload.model_dump(), headers=self.headers)

        document_id = json.loads(response.text).get("id")
        participant_id = (
            json.loads(response.text).get("participants")[0].get("id")
            if json.loads(response.text).get("participants")
            else None
        )

        if document_id:
            update_treatment_form(
                treatment_ids=treatment_ids,
                document_id=document_id,
                participant_id=participant_id,
                db=db,
            )
        else:
            raise ValueError(json.loads(response.text).get("title"))

        return self.get_sign_embedded_secure_link(
            redirect_url="https://skinbeam-hongkong.feynman-crm.mementoai.io/customer/1#consultation",
            document_id=document_id,
            participant_id=participant_id,
        )

    # 시술 동의서 템플릿 웹훅 service
    def consent_sign_webhook(self, master: str, request: CreateSignWebhookRequest, db: Session) -> None:
        consent_form = sign_crud.get_consent_form_by_document_id(request.document.id, db)

        if request.event.type == SignDocumentStatusEnum.STARTED:
            consent_form.status = SignDocumentStatusEnum.STARTED
        elif request.event.type.is_signed():
            consent_form.status = SignDocumentStatusEnum.SIGNED
            consent_form.signed_at = datetime.now(tz=UTC)

            self.update_document_url(
                master=master, document_id=request.document.id, form_type=FormTypeEnum.CONSENT, db=db
            )
        else:
            consent_form.status = SignDocumentStatusEnum.ETC

        db.commit()

        return None

    # 의사용 시술 전자서명 템플릿 웹훅 service
    def treatment_sign_webhook(self, master: str, request: CreateSignWebhookRequest, db: Session) -> None:
        treatment_form = get_treatment_form_by_document_id(document_id=request.document.id, db=db)

        if request.event.type == SignDocumentStatusEnum.STARTED:
            treatment_form.status = SignDocumentStatusEnum.STARTED
        elif request.event.type.is_signed():
            treatment_form.status = SignDocumentStatusEnum.SIGNED
            treatment_form.signed_at = datetime.now(tz=UTC)

            self.update_document_url(
                master=master, document_id=request.document.id, form_type=FormTypeEnum.TREATMENT, db=db
            )
        else:
            treatment_form.status = SignDocumentStatusEnum.ETC

        db.commit()

        return None

    # 전자서명 문서 url 생성 service
    def update_document_url(self, master: str, document_id: str, form_type: FormTypeEnum, db: Session) -> dict:
        DOCUMENT_URL = f"https://api.modusign.co.kr/documents/{document_id}"

        headers = {"accept": "application/json", "authorization": f"Basic {settings.MODUSIGN_ACCESS_KEY}"}

        response = requests.get(DOCUMENT_URL, headers=headers)
        json_response = json.loads(response.text)
        downloadUrl = json_response.get("file").get("downloadUrl")

        uploader = S3Uploader()

        file_name = f"{master}/sign-document/{form_type}/{uuid.uuid1()}"

        image_url = uploader.upload_file_from_url(downloadUrl, file_name)

        if form_type == FormTypeEnum.CONSENT:
            consent_form = sign_crud.get_consent_form_by_document_id(document_id, db)
            consent_form.document_url = image_url
        else:
            treatment_form = get_treatment_form_by_document_id(document_id, db)
            treatment_form.document_url = image_url

        db.flush()

        return json.loads(response.text)
