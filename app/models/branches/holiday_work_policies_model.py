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

class HolidayWorkPolicies(Base): #휴무일 근무 여부 설정
    __tablename__ = "holiday_work_policies"
    # __table_args__ = (
    #     Index('idx_part_policies_branch_id', 'branch_id'),
    #     Index('idx_part_policies_branch_policy_id', 'branch_policy_id'),
    # )
    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    do_holiday_work = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")