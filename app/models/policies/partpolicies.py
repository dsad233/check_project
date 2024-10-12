from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base

class PartWorkPolicies(Base):
    __tablename__ = "part_work_policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    work_policy_id = Column(Integer, ForeignKey("work_policies.id"), nullable=False)
    work_start_time = Column(DateTime, nullable=True)
    work_end_time = Column(DateTime, nullable=True)
    lunch_start_time = Column(DateTime, nullable=True)
    lunch_end_time = Column(DateTime, nullable=True)
    break_time_1 = Column(String(50), nullable=True)
    break_time_2 = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    part = relationship("Parts", back_populates="part_work_policies")
    work_policy = relationship("WorkPolicies", back_populates="part_work_policies")


class PartSalaryPolicies(Base):
    __tablename__ = "part_salary_policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    salary_policy_id = Column(Integer, ForeignKey("salary_policies.id"), nullable=False)
    base_salary = Column(Integer, nullable=True)
    annual_leave_days = Column(Integer, nullable=True)
    sick_leave_days = Column(Integer, nullable=True)
    overtime_rate = Column(Float, nullable=True)
    night_work_allowance = Column(Integer, nullable=True)
    holiday_work_allowance = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    part = relationship("Parts", back_populates="part_salary_policies")
    salary_policy = relationship("SalaryPolicies", back_populates="part_salary_policies")