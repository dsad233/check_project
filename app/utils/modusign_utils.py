from datetime import datetime

from app.enums.modusign import SIGNINGMETHOD_OBJECT_TYPE
from app.models.users.users_model import Users
from app.schemas.modusign_schemas import TemplateResponse


class ModuSignGenerator:
    @staticmethod
    def convert_template_response_to_document_data(
            template_response: TemplateResponse,
            user: Users,
    ) -> dict:
        today = datetime.today()
        image_path = "/Users/marin/Downloads/signature.jpg"

        return {
            "templateId": template_response.id,
            "document": {
                "title": template_response.title,
                # "title": f"{user.name} 근로 계약서",
                "participantMappings": [
                    {
                        "signingMethod": {
                            "type": SIGNINGMETHOD_OBJECT_TYPE.KAKAO,
                            "value": user.phone_number.replace("-", "")
                        },
                        "role": participant.role,
                        "name": user.name
                    }
                    for participant in template_response.participants
                ],
                "requesterInputMappings": [
                    {
                        "dataLabel": "employer",
                        "value": user.branch.representative_name
                    },
                    {
                        "dataLabel": "employee1",
                        "value": user.name
                    },
                    {
                        "dataLabel": "contractPeriod",
                        "value": str(user.hire_date)
                    },
                    {
                        "dataLabel": "companyAddress1",
                        "value": user.branch.name
                    },
                    {
                        "dataLabel": "work",
                        "value": user.part.name
                    },
                    {
                        "dataLabel": "employeeEmail",
                        "value": user.email
                    },
                    {
                        "dataLabel": "yyyy",
                        "value": str(today.year)
                    },
                    {
                        "dataLabel": "mm",
                        "value": str(today.month)
                    },
                    {
                        "dataLabel": "dd",
                        "value": str(today.day)
                    },
                    {
                        "dataLabel": "employee2",
                        "value": user.name
                    },
                    {
                        "dataLabel": "company",
                        "value": user.branch.name
                    },
                    {
                        "dataLabel": "representative",
                        "value": user.branch.representative_name
                    },
                    {
                        "dataLabel": "companyAddress2",
                        "value": user.branch.address
                    },
                    {
                        "dataLabel": "employee3",
                        "value": user.name
                    },
                    {
                        "dataLabel": "employeeBirth",
                        "value": str(user.birth_date)
                    },
                    # {
                    #     "dataLabel": "representativeSignature",
                    #     "value": image_to_base64(image_path, "jpg")
                    # }
                ]
            }
        }

