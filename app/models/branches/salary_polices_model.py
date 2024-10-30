from datetime import datetime
from typing import Optional, List  # typing에서 Optional과 List 임포트
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from app.core.database import Base
from pydantic import BaseModel, Field

from app.models.branches.allowance_policies_model import AllowancePoliciesResponse
from app.models.branches.parttimer_policies_model import ParttimerPoliciesDto


class SalaryTemplatesPolicies(Base):
    """
    임금 명세서 설정 모델
    
    parts 테이블과 1:1 관계
    """
    __tablename__ = "salary_templates_policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False, unique=True)
    
    # 파트별 수당 정책
    unused_annual_leave_allowance = Column(Boolean, default=False)  # 미사용 연차 수당
    additional_overtime_allowance = Column(Boolean, default=False)  # 추가 시간외 수당
    additional_holiday_allowance = Column(Boolean, default=False)  # 추가 휴일 수당
    annual_leave_deduction = Column(Boolean, default=False)  # 연차사용공제
    attendance_deduction = Column(Boolean, default=False)  # 근태공제
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class SalaryTemplatesPoliciesDto(BaseModel):
    branch_id: Optional[int] = None
    part_id: Optional[int] = None
    part_name: Optional[str] = None
    unused_annual_leave_allowance: bool = Field(description="미사용 연차 수당", default=False)
    additional_overtime_allowance: bool = Field(description="추가 시간외 수당", default=False)
    additional_holiday_allowance: bool = Field(description="추가 휴일 수당", default=False)
    annual_leave_deduction: bool = Field(description="연차사용공제", default=False)
    attendance_deduction: bool = Field(description="근태공제", default=False)

    class Config:
        from_attributes = True
        

class CombinedPoliciesResponse(BaseModel):
    parttimer_policies: ParttimerPoliciesDto | None = None
    salary_templates_policies: list[SalaryTemplatesPoliciesDto] | None = None  # 리스트 타입으로 변경
    allowance_policies: AllowancePoliciesResponse | None = None

    class Config:
        from_attributes = True

class CombinedPoliciesUpdate(BaseModel):
    parttimer_policies: Optional[ParttimerPoliciesDto] = None
    salary_templates_policies: Optional[List[SalaryTemplatesPoliciesDto]] = None
    allowance_policies: Optional[AllowancePoliciesResponse] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "parttimer_policies": {
                    "branch_id": 1,
                    "weekday_base_salary": True,
                    "remote_base_salary": True,
                    "annual_leave_allowance": True,
                    "overtime_allowance": True,
                    "holiday_work_allowance": True
                },
                "salary_templates_policies": [
                    {
                        "branch_id": 1,
                        "part_id": 1,
                        "unused_annual_leave_allowance": True,
                        "additional_overtime_allowance": True,
                        "additional_holiday_allowance": True,
                        "annual_leave_deduction": True,
                        "attendance_deduction": True
                    }
                ],
                "allowance_policies": {
                    "branch_id": 1,
                    "payment_day": 10,
                    "job_duty": True,
                    "meal": True,
                    "base_salary": True
                }
            }
        }
