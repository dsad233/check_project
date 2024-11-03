from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BaseSearchDto(BaseModel):
    page: Optional[int] = Field(default=1, description="현재 페이지 번호", ge=0)
    offset: Optional[int] = Field(default=0, description="시작 행")
    record_size: Optional[int] = Field(default=10, description="출력 갯수", gt=0)

    def __init__(self, **data):
        super().__init__(**data)
        self.offset = (self.page - 1) * self.record_size


class NamePhoneSearchDto(BaseSearchDto):
    name: Optional[str] = None
    phone_number: Optional[str] = None


class PostSearchDto(BaseSearchDto):
    branch_id: int
    search_type: str
    keyword: str


class LeaveSearchDto(BaseSearchDto):
    branch_id: int
    category_id: int
    status: str
    name: str
    phone_number: str


class OTSearchDto(BaseSearchDto):
    branch_id: int
    category_id: int
    status: str
    name: str
    phone_number: str


class WorkSearchDto(BaseSearchDto):
    branch_id: int
    category_id: int
    status: str
    name: str
    phone_number: str


class DocumentSearchDto(BaseSearchDto):
    branch_id: int
    category_id: int
    status: str
    name: str
    phone_number: str


class PaySearchDto(BaseSearchDto):
    branch_id: int
    part_id: int
    user_id: int
    name: str
    phone_number: str
