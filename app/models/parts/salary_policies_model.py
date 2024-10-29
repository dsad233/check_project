from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from pydantic import Field
from pydantic_settings import BaseSettings


class SalaryPolicies(Base):
    __tablename__ = "salary_policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    base_salary = Column(Integer, nullable=True)
    annual_leave_days = Column(Integer, nullable=True)
    sick_leave_days = Column(Integer, nullable=True)
    overtime_rate = Column(Float, nullable=True)
    night_work_allowance = Column(Integer, nullable=True)
    holiday_work_allowance = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)




class SalaryPoliciesCreate(BaseSettings):
    base_salary : str = Field("월급")