from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Boolean
from app.core.database import Base
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import relationship
from datetime import datetime


class ClosedDays(Base):
    __tablename__ = "closed_days"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=True, index=True)
    part_id = Column(Integer, ForeignKey('parts.id'), nullable=True)
    user_id = Column(Integer,ForeignKey('users.id'), nullable=True)
    closed_day_date = Column(Date, nullable=False, index=True)
    memo = Column(String(500))
    is_sunday = Column(Boolean, default= False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    


class ClosedDayBase(BaseModel):

    closed_day_date: Optional[date] = Field(None, description="휴무일 날짜")
    memo: Optional[str] = Field(None, max_length=500, description="휴무일에 대한 메모")

    @field_validator("closed_day_date")
    @classmethod
    def validate_date(cls, v):
        if v is not None and v < date.today():
            raise ValueError("휴무일은 오늘 이후의 날짜여야 합니다.")
        return v

    @field_validator("memo")
    @classmethod
    def validate_memo(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError("메모는 비어있을 수 없습니다.")
        return v


class ClosedDayCreate(ClosedDayBase):
    closed_day_date: date = Field(..., description="휴무일 날짜")
    memo : Optional[str] = Field(None, description= "휴무일에 대한 메모")

    class Config:
        from_attributes = True


class ClosedDayUpdate(ClosedDayBase):
    pass
