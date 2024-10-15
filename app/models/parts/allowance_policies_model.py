from datetime import datetime

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
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from pydantic_settings import BaseSettings
from typing import Optional


class AllowancePolicies(Base):
    __tablename__ = "allowance_policies"
    # __table_args__ = (
    #     Index('idx_part_policies_part_id', 'part_id')
    # )
    id = Column(Integer, primary_key=True, autoincrement=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)

    comprehensive_overtime = Column(Boolean, default=False)  # 포괄산정 연장근무수당
    annual_leave = Column(Boolean, default=False)  # 연차수당
    holiday_work = Column(Boolean, default=False)  # 휴일수당
    job_duty = Column(Boolean, default=False)  # 직무수당
    meal = Column(Boolean, default=False)  # 식대

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    branch = relationship("Branches", back_populates="allowance_policies")
    
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