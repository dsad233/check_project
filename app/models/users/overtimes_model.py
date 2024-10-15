from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import Column, Date, DateTime, Enum, Float, ForeignKey, Integer, String

from app.core.database import Base


class Overtimes(Base):
    __tablename__ = "overtimes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    overtime_hours = Column(Enum("30", "60", "90", "120", name="overtime_hours_options"), nullable=False)
    status = Column(Enum("pending", "approved", "rejected", name="overtime_status"), nullable=False, default="pending")
    application_date = Column(Date, nullable=False, default=datetime.now(UTC).date())
    application_memo = Column(String(500), nullable=True)
    manager_memo = Column(String(500), nullable=True)
    processed_date = Column(Date, nullable=True)
    is_approved = Column(String(1), default="N")

    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    deleted_yn = Column(String(1), default="N")


from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class OvertimeBase(BaseModel):
    applicant_id: Optional[int] = Field(None, description="신청자 ID")
    manager_id: Optional[int] = Field(None, description="승인자 ID")
    overtime_hours: Optional[str] = Field(None, description="초과 근무 시간")
    status: Optional[str] = Field(None, description="상태")
    application_memo: Optional[str] = Field(None, max_length=500, description="신청 메모")
    manager_memo: Optional[str] = Field(None, max_length=500, description="승인자 메모")
    processed_date: Optional[datetime] = Field(None, description="처리 일자")
    is_approved: Optional[str] = Field(None, description="승인 여부")

class OvertimeCreate(BaseModel):
    overtime_hours: str = Field(..., description="초과 근무 시간")
    application_memo: str = Field(None, max_length=500, description="신청 메모")
    
    @field_validator("overtime_hours")
    def validate_overtime_hours(cls, v):
        if v is not None and int(v) < 0:
            raise ValueError("초과 근무 시간은 0 이상이어야 합니다.")
        return v
    
    @field_validator("overtime_hours")
    def validate_overtime_hours_options(cls, v):
        if v is not None and v not in ["30", "60", "90", "120"]:
            raise ValueError("초과 근무 시간은 30, 60, 90, 120 중 하나여야 합니다.")
        return v
    
    @field_validator("application_memo")
    def validate_application_memo(cls, v):
        if v is not None and len(v) > 500 and len(v) < 1:
            raise ValueError("신청 메모는 1자 이상 500자 이하여야 합니다.")
        return v
