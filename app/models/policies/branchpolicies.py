from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Boolean, Float, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class BranchPolicies(Base):
    __tablename__ = "branch_policies"

    id = Column(Integer, primary_key=True)
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    name = Column(String(255), nullable=False)
    policy_type = Column(Enum('근태', '직책', '상담실적', '의사', '예산', name='policy_type'), nullable=False)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default='N')

    branch = relationship("Branches", back_populates="branch_policies")
    work_policies = relationship("WorkPolicies", back_populates="branch_policy")
    salary_policies = relationship("SalaryPolicies", back_populates="branch_policy")
    document_policies = relationship("DocumentPolicies", back_populates="branch_policy")
    part_policies = relationship("PartPolicies", back_populates="branch_policy")

class DocumentPolicies(Base):
    __tablename__ = "document_policies"

    id = Column(Integer, primary_key=True)
    branch_policy_id = Column(Integer, ForeignKey('branch_policies.id'), nullable=False)
    document_type = Column(String(255), nullable=False)
    can_view = Column(Boolean, default=False)
    can_edit = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default='N')

    branch_policy = relationship("BranchPolicies", back_populates="document_policies")

class WorkPolicies(Base):
    __tablename__ = "work_policies"

    id = Column(Integer, primary_key=True)
    branch_policy_id = Column(Integer, ForeignKey('branch_policies.id'), nullable=False)
    work_start_time = Column(DateTime, nullable=False)
    work_end_time = Column(DateTime, nullable=False)
    lunch_start_time = Column(DateTime, nullable=False)
    lunch_end_time = Column(DateTime, nullable=False)
    break_time_1 = Column(String(50), nullable=True)
    break_time_2 = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default='N')

    branch_policy = relationship("BranchPolicies", back_populates="work_policies")
    part_work_policies = relationship("PartWorkPolicies", back_populates="work_policy")

class SalaryPolicies(Base):
    __tablename__ = "salary_policies"

    id = Column(Integer, primary_key=True)
    branch_policy_id = Column(Integer, ForeignKey('branch_policies.id'), nullable=False)
    base_salary = Column(Integer, nullable=False)
    annual_leave_days = Column(Integer, nullable=False)
    sick_leave_days = Column(Integer, nullable=False)
    overtime_rate = Column(Float, nullable=False)
    night_work_allowance = Column(Integer, nullable=False)
    holiday_work_allowance = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default='N')

    branch_policy = relationship("BranchPolicies", back_populates="salary_policies")
    part_salary_policies = relationship("PartSalaryPolicies", back_populates="salary_policy")

class PartPolicies(Base):
    __tablename__ = "part_policies"

    id = Column(Integer, primary_key=True)
    branch_policy_id = Column(Integer, ForeignKey('branch_policies.id'), nullable=False)
    part_id = Column(Integer, ForeignKey('parts.id'), nullable=False)
    policy_details = Column(String(500), nullable=True)
    structure = Column(String(255), nullable=True)
    group = Column(String(255), nullable=True)
    auto_calculation = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default='N')

    branch_policy = relationship("BranchPolicies", back_populates="part_policies")
    part = relationship("Parts", back_populates="part_policies")