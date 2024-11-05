from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.enums.users import TimeOffType


class TimeOffResponseDto(BaseModel):
    id: int
    user_id: int
    time_off_type: Optional[TimeOffType] = Field(default=None, description="휴가 유형")
    start_date: Optional[datetime] = Field(default=None, description="휴가 시작일")
    end_date: Optional[datetime] = Field(default=None, description="휴가 종료일")
    description: Optional[str] = Field(default=None, max_length=500, description="휴가 사유")
    is_paid: Optional[bool] = Field(default=None, description="유급 여부")

    model_config = ConfigDict(from_attributes=True)

# 이름, 지점명, 파트명, 신청일을 포함한 Dto
class TimeOffReadAllResponseDto(TimeOffResponseDto):
    name: str = Field(description="사용자 이름")
    branch_name: str = Field(description="지점명")
    part_name: str = Field(description="파트명")
    created_at: datetime = Field(description="신청일")

    model_config = ConfigDict(from_attributes=True)



class TimeOffBaseDto(BaseModel):
    time_off_type: TimeOffType
    start_date: datetime
    end_date: datetime
    is_paid: bool
    description: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class TimeOffCreateRequestDto(TimeOffBaseDto):
    user_id: int


class TimeOffUpdateRequestDto(BaseModel):
    time_off_type: Optional[TimeOffType] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] =None
    description: Optional[str] = None
    is_paid: Optional[bool] = None
    
    model_config = ConfigDict(from_attributes=True)







# class TimeOffListDto(BaseModel):
#     id: int
#     branch_name: str
#     part_name: str
#     created_at: date
#     time_off_type: TimeOffType
#     start_date: date
#     end_date: date
#     description: str


# class TimeOffListResponse(BaseModel):
#     time_offs: list[TimeOffListDto]
