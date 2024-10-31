"""
{
  "event": {
    "type": "document_all_signed"
  },
  "document": {
    "id": "{DOCUMENT_ID}",
    "requester": {
      "email": "{REQUESTER_EMAIL}"
    }
  }
}
"""
from pydantic import BaseModel


class Event(BaseModel):
    type: str

class Document(BaseModel):
    id: str
    requester: dict

class DocumentAllSigned(BaseModel):
    event: Event
    document: Document