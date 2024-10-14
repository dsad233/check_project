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


class CommutePolicies(Base): #출퇴근 설정 (출퇴 사용여부 설정 / IP 출퇴근 사용여부 설정도 있으나, MVP단계에서는 고려할 필요 없음)
    __tablename__ = "commute_policies"
    __table_args__ = (
        Index('idx_commute_policies_branch_id', 'branch_id'),
        Index('idx_commute_policies_branch_policy_id', 'branch_policy_id'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    branch_policy_id = Column(Integer, ForeignKey("branch_policies.id"), nullable=False)
    do_commute = Column(Boolean, default=False)
    allowed_ip_commute = Column(String(255), nullable=True) # 여러 아이피 주소를 쉼표로 구분해서 저장
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    branch = relationship("Branches", back_populates="commute_policies")
    branch_policy = relationship("BranchPolicies", back_populates="commute_policies")