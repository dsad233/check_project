from pydantic import BaseModel
from typing import Optional
from app.common.dto.pagination_dto import PaginationDto


class UserLeaveResponse(BaseModel):
    id: Optional[int]
    name: Optional[str]
    part_name: Optional[str]
    grant_type: Optional[str]
    total_leave_days: Optional[int]


class UsersLeaveResponse(BaseModel):
    data: list[UserLeaveResponse]
    pagination: PaginationDto

