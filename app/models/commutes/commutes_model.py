from typing import Dict, List, Optional
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, func
from fastapi import HTTPException

from app.core.database import Base
from pydantic_settings import BaseSettings

from pydantic import BaseModel, Field, field_validator


class Commutes(Base):
    __tablename__ = "commutes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    clock_in = Column(DateTime, nullable=False, default=datetime.now(UTC))
    clock_out = Column(DateTime)
    work_hours = Column(Float)
    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    deleted_yn = Column(String(1), default="N")


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
        if v and "clock_in" in values.data and values.data["clock_in"]:
            if v <= values.data["clock_in"]:
                raise ValueError("퇴근 시간은 출근 시간보다 늦어야 합니다.")
        return v

    @field_validator("work_hours")
    @classmethod
    def calculate_work_hours(cls, v, values):
        if (
            "clock_in" in values.data
            and values.data["clock_in"]
            and "clock_out" in values.data
            and values.data["clock_out"]
        ):
            work_hours = (
                values.data["clock_out"] - values.data["clock_in"]
            ).total_seconds() / 3600
            return round(work_hours, 2)
        return v

    @field_validator("deleted_yn")
    @classmethod
    def validate_deleted_yn(cls, v):
        if v and v not in ["Y", "N"]:
            raise ValueError("삭제 여부는 'Y' 또는 'N'이어야 합니다.")
        return v

class Commutes_clock_in(BaseModel):
    clock_in : datetime = Field(default_factory=datetime.now)
    
    @field_validator("clock_in")
    @classmethod
    def validate_sunday_clock_in(cls, clock_in):
        if(clock_in.weekday() == 6):
            raise HTTPException(status_code=400, detail="일요일에는 출석, 퇴근 기록이 불가합니다.")
        return clock_in
    
class Commutes_clock_out(BaseModel):
    clock_out : datetime = Field(default_factory=datetime.now)
    updated_at : datetime = Field(default_factory=datetime.now)
    
    @field_validator("clock_out")
    @classmethod
    def validate_sunday_clock_out(cls, clock_out):
        if(clock_out.weekday() == 6):
            raise HTTPException(status_code=400, detail="일요일에는 출석, 퇴근 기록이 불가합니다.")
        return clock_out

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

    @field_validator("*")
    def check_at_least_one_field(cls, v, values):
        if not v and not any(values.data.values()):
            raise ValueError(
                "적어도 하나의 필드(퇴근 시간 또는 근무 시간)는 제공되어야 합니다."
            )
        return v
