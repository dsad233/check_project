from sqlalchemy import Column, DateTime, String, ForeignKey, Integer, Enum
from datetime import datetime
from app.enums.branches import TimeUnit
from app.core.database import Base
from pydantic import BaseModel, Field
from typing import Literal


class ConditionBasedAnnualLeaveGrant(Base):
    __tablename__ = "condition_based_annual_leave_grant"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    condition_based_month = Column(Integer, nullable=False, default=0)
    condition_based_cnt = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")
