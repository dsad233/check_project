from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")


class ResponseDTO(BaseModel):
    status: str
    message: str
    data: Any

    @classmethod
    def build(cls, status: str, message: str, data: Any = None) -> "ResponseDTO":
        return cls(status=status, message=message, data=data)
