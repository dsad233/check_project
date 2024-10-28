from sqlalchemy import Column, DateTime, String, ForeignKey, Integer, Enum
from datetime import datetime
from app.enums.branches import LeaveResetOption
from app.core.database import Base
from pydantic import BaseModel, Field
from typing import Literal


class EntryDateBasedAnnualLeaveGrant(Base):
    __tablename__ = "entry_date_based_annual_leave_grant"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    entry_date_based_remaining_leave = Column(
        Enum(*[e.value for e in LeaveResetOption]),
        nullable=False,
        default=LeaveResetOption.RESET.value,
        comment="매 년 입사일 기준",
    )
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")
