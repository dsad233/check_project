from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Index
)
from sqlalchemy.orm import relationship

from app.core.database import Base

class Parts(Base):
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    task = Column(String(500), nullable=True)
    is_doctor = Column(Boolean, default=False)
    required_certification = Column(Boolean, default=False)
    leave_granting_authority = Column(Boolean, default=False)

    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    branch = relationship("Branches", back_populates="parts")
    users = relationship("Users", back_populates="part")
    part_policies = relationship("PartPolicies", back_populates="part")
    part_work_policies = relationship("PartWorkPolicies", back_populates="part")
    part_salary_policies = relationship("PartSalaryPolicies", back_populates="part")
    hourly_wage_policies = relationship("HourlyWagePolicies", back_populates="part")
    rest_days = relationship("RestDays", back_populates="part")
    annual_leaves = relationship("AnnualLeave", back_populates="part")