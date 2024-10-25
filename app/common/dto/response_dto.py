from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

# 제네릭 타입 선언
T = TypeVar('T')

# Response DTO 선언
class ResponseDTO(BaseModel, Generic[T]):
    status: str
    message: Optional[str]
    data: Optional[T]

    @classmethod
    def build(cls, status: str, message: Optional[str], data: Optional[T]):
        return cls(status=status, message=message, data=data)
