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


class Branches(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    representative_name = Column(String(255), nullable=False)
    registration_number = Column(String(255), nullable=False)
    call_number = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    corporate_seal = Column(String(255), nullable=False)
    nameplate = Column(String(255), nullable=False)
    mail_address = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    users = relationship("Users", back_populates="branch")
    parts = relationship("Parts", back_populates="branch")
    branch_policies = relationship("BranchPolicies", back_populates="branch")
    part_work_policies = relationship("PartWorkPolicies", back_populates="branch")
    part_salary_policies = relationship("PartSalaryPolicies", back_populates="branch")
    document_policies = relationship("DocumentPolicies", back_populates="branch")
    work_policies = relationship("WorkPolicies", back_populates="branch")
    salary_policies = relationship("SalaryPolicies", back_populates="branch")
    part_policies = relationship("PartPolicies", back_populates="branch")
    commute_policies = relationship("CommutePolicies", back_populates="branch")
    overtime_policies = relationship("OverTimePolicies", back_populates="branch")
    auto_overtime_policies = relationship("AutoOvertimePolicies", back_populates="branch")
    holiday_work_policies = relationship("HolidayWorkPolicies", back_populates="branch")
    weekend_work_policies = relationship("WeekendWorkPolicies", back_populates="branch")
    allowance_policies = relationship("AllowancePolicies", back_populates="branch")
    hourly_wage_policies = relationship("HourlyWagePolicies", back_populates="branch")