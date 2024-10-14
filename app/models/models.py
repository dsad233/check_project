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
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.database import Base

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
    rest_days = relationship("RestDays", back_populates="branch")
    annual_leaves = relationship("AnnualLeave", back_populates="branch")

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
    annual_leaves = relationship("AnnualLeave", back_populates="user")

#________________________________________________________________________________________#
# 휴무일 테이블
class RestDays(Base):
    __tablename__ = "rest_days"
    __table_args__ = (
        Index('idx_rest_days_branch_id', 'branch_id'),
        Index('idx_rest_days_part_id', 'part_id'),
        Index('idx_rest_days_date', 'date'),
        UniqueConstraint('branch_id', 'part_id', 'date', name='uq_branch_part_date'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    date = Column(Date, nullable=False)
    rest_type = Column(Enum('공휴일', '주말', name='rest_day_type'), nullable=False)
    description = Column(String(255), nullable=True)
    is_paid = Column(Boolean, default=False)  # 유급 휴일 여부
    is_holiday_work_allowed = Column(Boolean, default=False)  # 휴일근무 허용 여부
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    branch = relationship("Branches", back_populates="rest_days")
    part = relationship("Parts", back_populates="rest_days")

#________________________________________________________________________________________#
# 연차 테이블   
class AnnualLeave(Base):
    __tablename__ = "annual_leave"
    __table_args__ = (
        Index('idx_annual_leave_user_id', 'user_id'),
        Index('idx_annual_leave_date', 'date'),
        UniqueConstraint('user_id', 'date', name='uq_user_date'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    leave_type = Column(Enum('유급휴가', '유급 오전반차', '유급 오후반차', '무급휴가', '무급 오전반차', '무급 오후반차', name='leave_type'), nullable=False)
    is_paid = Column(Boolean, nullable=False)
    description = Column(String(255), nullable=True)
    is_approved = Column(Boolean, default=False)  # 승인 여부
    is_leave_of_absence = Column(Boolean, default=False)  # 휴직 여부
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    user = relationship("Users", back_populates="annual_leaves")