from pydantic import BaseModel
from datetime import datetime

class BaseSearchDto(BaseModel):
    page: int # 현재 페이지
    offset: int # 출력 갯수
    limit: int # 시작 행

    def __init__(self, page: int = 1, limit: int = 0, offset: int = 10):
        self.page = page
        self.offset = offset
        self.limit = (self.page - 1) * self.offset

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