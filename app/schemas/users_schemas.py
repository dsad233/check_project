from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional
from app.common.dto.pagination_dto import PaginationDto
from app.common.dto.search_dto import NamePhoneSearchDto
from datetime import date

class UserLeaveResponse(BaseModel):
    id: Optional[int]
    name: Optional[str]
    part_name: Optional[str]
    grant_type: Optional[str]
    total_leave_days: Optional[int]


class UsersLeaveResponse(BaseModel):
    data: list[UserLeaveResponse]
    pagination: PaginationDto


class PersonnelRecordHistoryCreateRequest(BaseModel): 
    personnel_record_category_id: int
    worker_comment: str
    admin_comment: str
    created_at: date
    

class PersonnelRecordHistoryCreateResponse(BaseModel):
    id: int
    personnel_record_category_id: int
    worker_comment: str
    admin_comment: str
    created_at: date

    model_config = ConfigDict(from_attributes=True)


class PersonnelRecordHistoryUpdateRequest(BaseModel):
    personnel_record_category_id: int
    worker_comment: str
    admin_comment: str
    created_at: date


class PersonnelRecordHistoryResponse(BaseModel):
    id: int
    user_name: str
    created_by_user_name: str
    personnel_record_category_name: str
    worker_comment: str
    admin_comment: str
    created_at: date


class PersonnelRecordHistoriesResponse(BaseModel):
    data: list[PersonnelRecordHistoryResponse]
    pagination: PaginationDto


class PersonnelRecordUsersRequest(NamePhoneSearchDto):
    branch_id: Optional[int] = None
    part_id: Optional[int] = None


class PersonnelRecordUserResponse(BaseModel):
    id: int
    name: str
    gender: str
    branch_name: str
    part_name: str
    weekly_work_days: Optional[int]
    recent_personnel_record_history_date: Optional[date]


class PersonnelRecordUsersResponse(BaseModel):
    data: list[PersonnelRecordUserResponse]
    pagination: PaginationDto


class UserNameResponse(BaseModel):
    id: int
    name: str


class UsersNameResponse(BaseModel):
    data: list[UserNameResponse]
    pagination: PaginationDto
