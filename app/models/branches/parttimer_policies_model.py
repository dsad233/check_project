from datetime import datetime
from typing import Optional
from pydantic import Field, BaseModel
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from app.core.database import Base


class ParttimerPolicies(Base):
    __tablename__ = "parttimer_policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    # 기본급 설정
    weekday_base_salary = Column(Boolean, default=False)  # 기본급(평일) 사용여부
    remote_base_salary = Column(Boolean, default=False)  # 기본급(재택) 사용여부
    
    # 수당 설정
    annual_leave_allowance = Column(Boolean, default=False)  # 연차수당 사용여부
    overtime_allowance = Column(Boolean, default=False)  # 연장근로수당 사용여부
    holiday_work_allowance = Column(Boolean, default=False)  # 휴일근로수당 사용여부

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class ParttimerPoliciesDto(BaseModel):
    branch_id: Optional[int] = None
    weekday_base_salary: bool = Field(description="기본급(평일) 사용여부", default=False)
    remote_base_salary: bool = Field(description="기본급(재택) 사용여부", default=False)
    annual_leave_allowance: bool = Field(description="연차수당 사용여부", default=False)
    overtime_allowance: bool = Field(description="연장근로수당 사용여부", default=False)
    holiday_work_allowance: bool = Field(description="휴일근로수당 사용여부", default=False)

    class Config:
        from_attributes = True
