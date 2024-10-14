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
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.policies.branchpolicies import BranchPolicies


class Branches(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
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


class Parts(Base):
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    task = Column(String(500), nullable=True)
    is_doctor = Column(Boolean, default=False)
    required_certification = Column(String(500), nullable=True)
    leave_granting_authority = Column(String(500), nullable=True)

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


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)
    address = Column(String(500), nullable=True)
    education = Column(String(255), nullable=True)
    birth_date = Column(Date, nullable=True)
    hire_date = Column(Date, nullable=True)
    resignation_date = Column(Date, nullable=True)
    gender = Column(Enum("남자", "여자", name="user_gender"), nullable=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)

    last_company = Column(String(255), nullable=True)
    last_position = Column(String(255), nullable=True)
    last_career_start_date = Column(Date, nullable=True)
    last_career_end_date = Column(Date, nullable=True)

    role = Column(
        Enum(
            "MSO 최고권한", "최고관리자", "관리자", "사원", "퇴사자", name="user_role"
        ),
        nullable=False,
        default="사원",
    )

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    part = relationship("Parts", back_populates="users")
    branch = relationship("Branches", back_populates="users")
