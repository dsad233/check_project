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

class OverTimePolicies(Base): #연장근무 설정
    __tablename__ = "overtime_policies"
    # __table_args__ = (
    #     Index('idx_part_policies_branch_id', 'branch_id'),
    #     Index('idx_part_policies_branch_policy_id', 'branch_policy_id'),
    # )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    name = Column(String(255), nullable=False)  # 예: 의사, 간호사...
    
    # 연장근무 당 지급 금액 설정
    ot_30 = Column(Integer, nullable=False)
    ot_60 = Column(Integer, nullable=False)
    ot_90 = Column(Integer, nullable=False)
    ot_120 = Column(Integer, nullable=False)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")