from app.service.template_service import TemplateService as ModusignTemplateService
from app.service.document_service import DocumentService as ModusignDocumentService


# Modusign
def get_modusign_document_service():
    return ModusignDocumentService()

def get_modusign_template_service():
    return ModusignTemplateService()