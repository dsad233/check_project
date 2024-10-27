from pydantic import BaseModel
from typing import Generic, Optional, TypeVar

# 제네릭 타입 변수 선언
T = TypeVar("T")

class ResponseDTO(BaseModel, Generic[T]):
    status: str
    message: str
    data: Optional[T] = None
