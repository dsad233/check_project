from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class CommuteBase(BaseModel):
    user_id: Optional[int] = Field(None, description="사용자 ID")
    clock_in: Optional[datetime] = Field(None, description="출근 시간")
    clock_out: Optional[datetime] = Field(None, description="퇴근 시간")
    work_hours: Optional[float] = Field(None, description="근무 시간")
    updated_at: Optional[datetime] = Field(None, description="수정 일자")
    deleted_yn: Optional[str] = Field(None, description="삭제 여부")

    @field_validator("clock_out")
    @classmethod
    def validate_clock_out(cls, v, values):
        if v and 'clock_in' in values.data and values.data['clock_in']:
            if v <= values.data['clock_in']:
                raise ValueError("퇴근 시간은 출근 시간보다 늦어야 합니다.")
        return v

    @field_validator("work_hours")
    @classmethod
    def calculate_work_hours(cls, v, values):
        if 'clock_in' in values.data and values.data['clock_in'] and 'clock_out' in values.data and values.data['clock_out']:
            work_hours = (values.data['clock_out'] - values.data['clock_in']).total_seconds() / 3600
            return round(work_hours, 2)
        return v

    @field_validator("deleted_yn")
    @classmethod
    def validate_deleted_yn(cls, v):
        if v and v not in ['Y', 'N']:
            raise ValueError("삭제 여부는 'Y' 또는 'N'이어야 합니다.")
        return v


class CommuteUpdate(BaseModel):
    clock_out: Optional[datetime] = Field(None, description="퇴근 시간")
    work_hours: Optional[float] = Field(None, description="근무 시간")

    @field_validator("clock_out")
    def validate_clock_out(cls, v):
        if v > datetime.now():
            raise ValueError("퇴근 시간은 현재 시간보다 늦을 수 없습니다.")
        return v

    @field_validator("work_hours")
    def validate_work_hours(cls, v):
        if v is not None and v < 0:
            raise ValueError("근무 시간은 0 이상이어야 합니다.")
        return v

    @field_validator('*')
    def check_at_least_one_field(cls, v, values):
        if not v and not any(values.data.values()):
            raise ValueError("적어도 하나의 필드(퇴근 시간 또는 근무 시간)는 제공되어야 합니다.")
        return v
