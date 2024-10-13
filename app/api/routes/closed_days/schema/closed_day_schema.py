from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ClosedDayCreate(BaseModel):
    closed_day_date: date = Field(..., description="휴무일 날짜")
    memo: Optional[str] = Field(None, max_length=500, description="휴무일에 대한 메모")

    class Config:
        from_attributes = True

    @field_validator("closed_day_date")
    @classmethod
    def validate_date(cls, v):  # cls : 클래스, v : value(값)
        if v < date.today():
            raise ValueError("휴무일은 오늘 이후의 날짜여야 합니다.")
        return v

    @field_validator("memo")
    @classmethod
    def validate_memo(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError("메모는 비어있을 수 없습니다.")
        return v
