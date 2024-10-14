from pydantic import BaseModel, Field
from datetime import datetime

class BaseSearchDto(BaseModel):
    page: int = Field(default=1, description="현재 페이지")
    offset: int = Field(default=0, description="시작 행")
    record_size: int = Field(default=10, description="출력 갯수")

    def __init__(self, **data):
        super().__init__(**data)
        self.offset = (self.page - 1) * self.record_size

class PostSearchDto(BaseSearchDto):
    branch_id: int
    name: str
    phone_number: str

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