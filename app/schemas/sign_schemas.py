from fastapi import Query

from feynman_api.app.common.schemas import CamelAliasModel

from ..constants import NationEnum, SignChannelEnum, SignDocumentStatusEnum


class ConsentFormTypesRequest(CamelAliasModel):
    name: str | None = Query(None)


class ConsentFormTypesResponse(CamelAliasModel):
    class ConsentFormType(CamelAliasModel):
        id: int
        name: str
        nation: NationEnum
        is_self: bool
        template_id: str

    data: list[ConsentFormType]


class CreateConsentFormRequest(CamelAliasModel):
    booking_id: int
    consent_form_type_id: int
    sign_method_type: SignChannelEnum
    sign_method_value: str


class CreateSignWebhookRequest(CamelAliasModel):
    class EventObj(CamelAliasModel):
        type: SignDocumentStatusEnum

    class DocumentObj(CamelAliasModel):
        id: str

        class RequesterObj(CamelAliasModel):
            email: str

        requester: RequesterObj

    event: EventObj
    document: DocumentObj


class DeleteConsentFormsRequest(CamelAliasModel):
    consent_form_ids: list[int]
