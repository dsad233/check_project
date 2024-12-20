from datetime import datetime
from pydantic import Field, BaseModel
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class AutoOvertimePolicies(Base):
    __tablename__ = "auto_overtime_policies"
    # __table_args__ = (
    #     Index('idx_part_policies_branch_id', 'branch_id'),
    #     Index('idx_part_policies_branch_policy_id', 'branch_policy_id'),
    # )
    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    top_auto_applied = Column(Boolean, default=False)
    total_auto_applied = Column(Boolean, default=False)
    part_auto_applied = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")
