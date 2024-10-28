from sqlalchemy import Column, DateTime, String, ForeignKey, Integer, Enum
from datetime import datetime
from app.enums.branches import LeaveResetOption, LeaveGrantOption, DecimalRoundingPolicy
from app.core.database import Base
from pydantic import BaseModel, Field
from typing import Literal


class AccountBasedAnnualLeaveGrant(Base):
    __tablename__ = "account_based_annual_leave_grant"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    account_based_january_1st = Column(
        Enum(*[e.value for e in LeaveResetOption]),
        nullable=False,
        default=LeaveResetOption.RESET.value,
        comment="매 년 1월 1일기준",
    )
    account_based_less_than_year = Column(
        Enum(*[e.value for e in LeaveGrantOption]),
        nullable=False,
        default=LeaveGrantOption.SAME_YEAR_GRANT.value,
        comment="근속년수 1년 미만",
    )
    account_based_decimal_point = Column(
        Enum(*[e.value for e in DecimalRoundingPolicy]),
        nullable=False,
        default=DecimalRoundingPolicy.ROUND_UP_0_5.value,
        comment="소수점처리",
    )
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")
