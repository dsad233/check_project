from datetime import datetime
from pydantic import Field, BaseModel, ConfigDict
from pydantic_settings import BaseSettings
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    text
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class AllowancePolicies(Base):
    __tablename__ = "allowance_policies"
    # __table_args__ = (
    #     Index('idx_part_policies_part_id', 'part_id')
    # )
    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    payment_day = Column(Integer, nullable=False, default=10)  # 급여 지급일 (1-30)

    comprehensive_overtime = Column(Boolean, default=False)  # 포괄산정 연장근무수당 허용
    annual_leave = Column(Boolean, default=False)  # 연차수당 허용
    holiday_work = Column(Boolean, default=False)  # 휴일수당 허용
    job_duty = Column(Boolean, default=False)  # 직무수당 허용
    meal = Column(Boolean, default=False)  # 식대 허용
    base_salary = Column(Boolean, default=False, server_default=text('0'))  # 기본급 사용여부

    job_allowance = Column(Integer, nullable=True, default=0, server_default=text('0')) # 직무(직책)수당
    meal_allowance = Column(Integer, nullable=True, default=0, server_default=text('0')) # 식대
    doctor_holiday_work_pay = Column(Integer, nullable=False, default=0)  # 의사 휴일수당
    common_holiday_work_pay = Column(Integer, nullable=False, default=0)  # 일반 휴일수당
    
    is_additional_holiday_hundred = Column(Boolean, default=False) # 휴일 근로 수당 100원 단위
    is_unused_annual_leave_hundred = Column(Boolean, default=False) # 미사용 연차 수당 100원 단위
    is_annual_leave_deduction_hundred = Column(Boolean, default=False) # 연차사용공제 100원 단위
    is_attendance_deduction_hundred = Column(Boolean, default=False) # 근태공제 100원 단위
    
    display_meal_calc = Column(Boolean, default=False) # 식대 계산 표시
    display_night_calc = Column(Boolean, default=False) # 야간 수당 계산 표시

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")


class DefaultAllowancePoliciesDto(BaseModel):
    comprehensive_overtime: bool = Field(description="포괄산정 연장근무수당", default=False)
    annual_leave: bool = Field(description="연차수당", default=False)
    holiday_work: bool = Field(description="휴일수당", default=False)
    job_duty: bool = Field(description="직무수당", default=False)
    meal: bool = Field(description="식대", default=False)


    model_config = ConfigDict(from_attributes=True)
    
class HolidayAllowancePoliciesDto(BaseModel):
    doctor_holiday_work_pay: int = Field(description="의사 휴일수당", default=0)
    common_holiday_work_pay: int = Field(description="일반 휴일수당", default=0)

    model_config = ConfigDict(from_attributes=True)

class AllowancePoliciesDto(DefaultAllowancePoliciesDto, HolidayAllowancePoliciesDto):
    pass

class AllowancePoliciesResponse(BaseModel):
    branch_id: Optional[int] = None
    payment_day: Optional[int] = None
    job_duty: bool = Field(description="직무수당", default=False)
    meal: bool = Field(description="식대", default=False)
    base_salary: bool = Field(description="기본급 사용여부", default=False)
    
    is_additional_holiday_hundred: bool = Field(description="휴일 근로 수당 100원 단위", default=False)
    is_unused_annual_leave_hundred: bool = Field(description="미사용 연차 수당 100원 단위", default=False)
    is_annual_leave_deduction_hundred: bool = Field(description="연차사용공제 100원 단위", default=False)
    is_attendance_deduction_hundred: bool = Field(description="근태공제 100원 단위", default=False)
    
    display_meal_calc: bool = Field(description="식대 계산 표시", default=False)
    display_night_calc: bool = Field(description="야간 수당 계산 표시", default=False)

    model_config = ConfigDict(from_attributes=True)

class AllowancePoliciesCreate(BaseSettings):
    comprehensive_overtime : bool
    annual_leave : bool
    holiday_work : bool
    job_duty : bool
    meal : bool


class AllowancePoliciesUpdate(BaseSettings):
    comprehensive_overtime : Optional[bool] = None
    annual_leave : Optional[bool] = None
    holiday_work : Optional[bool] = None
    job_duty : Optional[bool] = None
    meal : Optional[bool] = None
    
    is_additional_holiday_hundred: Optional[bool] = None
    is_unused_annual_leave_hundred: Optional[bool] = None
    is_annual_leave_deduction_hundred: Optional[bool] = None
    is_attendance_deduction_hundred: Optional[bool] = None
    
    display_meal_calc: Optional[bool] = None
    display_night_calc: Optional[bool] = None
