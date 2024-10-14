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

# 근무설정 관련 테이블
class PartPolicies(Base): #파트 기본설정
    __tablename__ = "part_policies"
    __table_args__ = (
        Index('idx_part_policies_branch_id', 'branch_id'),
        Index('idx_part_policies_branch_policy_id', 'branch_policy_id'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    branch_policy_id = Column(Integer, ForeignKey("branch_policies.id"), nullable=False)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    policy_details = Column(String(500), nullable=True)
    structure = Column(String(255), nullable=True)
    group = Column(String(255), nullable=True)
    auto_calculation = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    branch = relationship("Branches", back_populates="part_policies")
    branch_policy = relationship("BranchPolicies", back_populates="part_policies")
    part = relationship("Parts", back_populates="part_policies")