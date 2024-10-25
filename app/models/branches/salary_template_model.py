from datetime import datetime, time
from typing import Optional
from pydantic import BaseModel, Field
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
    Time,
)
from app.core.database import Base
class SalaryTemplate(Base):
    __tablename__ = "salary_templates"
    id = Column(Integer, primary_key=True, autoincrement=True) #템플릿ID
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False) #회사ID
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False) #직책ID
    part_name = Column(String(255), nullable=False) #직책명
    name = Column(String(255), nullable=False) #템플릿명
    is_january_entry = Column(Boolean, nullable=False, default=False) #1월입사여부
    weekly_work_days = Column(Integer, nullable=False, default=5) #주간근무일수
    month_salary = Column(Integer, nullable=False, default=0) #월급
    included_holiday_allowance = Column(Boolean, nullable=False, default=False) #휴일수당포함여부
    included_job_allowance = Column(Boolean, nullable=False, default=False) #직책수당포함여부
    hour_wage = Column(Integer, nullable=False, default=0) #시급
    basic_salary = Column(Integer, nullable=False, default=0) #기본급여
    contractual_working_hours = Column(Integer, nullable=False, default=0) #소정근로시간
    weekly_rest_hours = Column(Integer, nullable=False, default=0) #주휴시간
    annual_salary = Column(Integer, nullable=False, default=0) #연봉
    comprehensive_overtime_allowance = Column(Integer, nullable=False, default=0) #포괄산정연장근무수당
    comprehensive_overtime_hour = Column(Integer, nullable=False, default=0) #포괄산정연장근무시간
    annual_leave_allowance = Column(Integer, nullable=False, default=0) #연차수당
    annual_leave_allowance_hour = Column(Integer, nullable=False, default=0) #연차수당시간
    annual_leave_allowance_day = Column(Integer, nullable=False, default=0) #연차수당일수

    holiday_allowance = Column(Integer, nullable=False, default=0) # 휴일수당 컬럼
    job_allowance = Column(Integer, nullable=False, default=0)# 직무(직책)수당 컬럼
    meal_allowance = Column(Integer, nullable=False, default=0)# 식대 컬럼
    hire_year = Column(Integer, nullable=False, default=0) # 입사년도 컬럼 ( 몇년도 기준 임금정책인지 )

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")


class SalaryTemplateDto(BaseModel):
    id: Optional[int] = Field(default=None, description="템플릿ID")
    part_id: int = Field(description="직책ID")
    part_name: str = Field(description="직책명")
    name: str = Field(description="템플릿명")
    is_january_entry: bool = Field(description="1월입사여부")
    weekly_work_days: int = Field(description="주간근무일수")
    month_salary: int = Field(description="월급")
    included_holiday_allowance: bool = Field(description="휴일수당포함여부")
    included_job_allowance: bool = Field(description="직책수당포함여부")
    hour_wage: int = Field(description="시급")
    basic_salary: int = Field(description="기본급여")
    contractual_working_hours: int = Field(description="소정근로시간")
    weekly_rest_hours: int = Field(description="주휴시간")
    annual_salary: int = Field(description="연봉")
    comprehensive_overtime_allowance: int = Field(description="포괄산정연장근무수당")
    comprehensive_overtime_hour: int = Field(description="포괄산정연장근무시간")
    annual_leave_allowance: int = Field(description="연차수당")
    annual_leave_allowance_hour: int = Field(description="연차수당시간")
    annual_leave_allowance_day: int = Field(description="연차수당일수")

    holiday_allowance: int = Field(description="휴일수당")
    job_allowance: int = Field(description="직무(직책)수당")
    meal_allowance: int = Field(description="식대")
    hire_year: int = Field(descriptio="입사년도 ( 몇년도 기준 임금정책인지 )")

    class Config:
        from_attributes = True