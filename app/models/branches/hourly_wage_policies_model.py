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
    Time,
    Float,
)
from sqlalchemy.orm import relationship

from app.core.database import Base

# 시급 설정 관련 테이블 #
class HourlyWagePolicies(Base):
    __tablename__ = "hourly_wage_policies"
    __table_args__ = (
        Index('idx_part_policies_branch_id', 'branch_id'),
        Index('idx_part_policies_branch_policy_id', 'branch_policy_id'),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    branch_policy_id = Column(Integer, ForeignKey("branch_policies.id"), nullable=False)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    
    work_start_time = Column(Time, nullable=False)
    work_end_time = Column(Time, nullable=False)
    break_time = Column(Integer, nullable=False)  # 휴게시간 (분 단위)
    hourly_wage = Column(Integer, nullable=False)  # 기본 시급
    
    additional_hourly_wage = Column(Integer, nullable=True)  # 추가 시급 (있는 경우)
    overtime_rate = Column(Float, nullable=True)  # 연장근무 할증률
    night_work_rate = Column(Float, nullable=True)  # 야간근무 할증률
    holiday_work_rate = Column(Float, nullable=True)  # 휴일근무 할증률
    
    is_common = Column(Boolean, default=False)  # 공통 정책 여부
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    branch = relationship("Branches", back_populates="hourly_wage_policies")
    branch_policy = relationship("BranchPolicies", back_populates="hourly_wage_policies")
    part = relationship("Parts", back_populates="hourly_wage_policies")