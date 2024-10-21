from datetime import datetime
from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings
from typing import Optional

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

from app.core.database import Base

class AutoAnnualLeaveApproval(Base):
    __tablename__ = "auto_annual_leave_approval"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)

    top_auto_approval = Column(Boolean, default=False)
    total_auto_approval = Column(Boolean, default=False)
    part_auto_approval = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

class AutoAnnualLeaveApprovalDto(BaseModel):
    top_auto_approval: bool = Field(description="통합관리자 자동승인", default=False)
    total_auto_approval: bool = Field(description="관리자 자동승인", default=False)
    part_auto_approval: bool = Field(description="사원 자동승인", default=False)

    class Config:
        from_attributes = True