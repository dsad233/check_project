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

# 급여 테이블 #
# 예를 들어 1000만원이 어떻게 나눠지는가에 대한 값이므로, 직접 설정하는 값이 아닙니다.
# 고정된 값들이 들어가게 됩니다.
class SalaryBracket(Base):
    __tablename__ = "salary_brackets"
    __table_args__ = (
        Index('idx_part_policies_branch_id', 'branch_id'),
        Index('idx_part_policies_branch_policy_id', 'branch_policy_id'),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    branch_policy_id = Column(Integer, ForeignKey("branch_policies.id"), nullable=False)
    base_salary = Column(Integer, nullable=False)
    monthly_salary = Column(Integer, nullable=False)
    daily_rate = Column(Integer, nullable=False)
    hourly_rate = Column(Integer, nullable=False)
    meal_allowance = Column(Integer, nullable=False)
    national_pension = Column(Integer, nullable=False)
    health_insurance = Column(Integer, nullable=False)
    employment_insurance = Column(Integer, nullable=False)
    income_tax = Column(Integer, nullable=False)
    local_income_tax = Column(Integer, nullable=False)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    branch = relationship("Branches", back_populates="salary_brackets")
    branch_policy = relationship("BranchPolicies", back_populates="salary_brackets")