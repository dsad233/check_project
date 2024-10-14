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

# 임금 설정 관련 테이블
# !! 대부분 직접 설정하는 게 아닌 앞서 설정한 기본설정 및 연봉 계산기를 통해서 자동으로 계산되는 부분들임에 유의 !!
class SalaryPolicies(Base):
    __tablename__ = "salary_policies"
    __table_args__ = (
        Index('idx_part_policies_branch_id', 'branch_id'),
        Index('idx_part_policies_branch_policy_id', 'branch_policy_id'),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    branch_policy_id = Column(Integer, ForeignKey("branch_policies.id"), nullable=False)
    base_salary = Column(Integer, nullable=False)
    meal_allowance = Column(Integer, nullable=True)
    position_allowance = Column(Integer, nullable=True)
    job_allowance = Column(Integer, nullable=True)
    overtime_allowance = Column(Integer, nullable=True)
    night_work_allowance = Column(Integer, nullable=True)
    holiday_work_allowance = Column(Integer, nullable=True)
    payment_day = Column(Integer, nullable=True)
    calculation_method = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    branch = relationship("Branches", back_populates="salary_policies")
    branch_policy = relationship("BranchPolicies", back_populates="salary_policies")
    part_salary_policies = relationship(
        "PartSalaryPolicies", back_populates="salary_policy"
    )