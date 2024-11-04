from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.enums.users import TimeOffType


class TimeOffGetResponseDto(BaseModel):
    id: int
    time_off_type: Optional[TimeOffType] = Field(
        default=None,
        description="휴가 유형"
    )
    start_date: Optional[datetime] = Field(
        default=None,
        description="휴가 시작일"
    )
    end_date: Optional[datetime] = Field(
        default=None,
        description="휴가 종료일"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="휴가 사유"
    )

    class Config:
        from_attributes = True

class TimeOffCreateRequestDto(BaseModel):
    user_id: int
    time_off_type: TimeOffType
    start_date: datetime
    end_date: datetime
    description: Optional[str] = None
    
    class Config:
        from_attributes = True




class TimeOffListDto(BaseModel):
    id: int
    branch_name: str
    part_name: str
    created_at: date
    time_off_type: TimeOffType
    start_date: date
    end_date: date
    description: str


class TimeOffListResponse(BaseModel):
    time_offs: list[TimeOffListDto]
