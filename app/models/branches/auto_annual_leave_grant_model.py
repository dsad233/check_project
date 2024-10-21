from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String
)

from app.core.database import Base

class AutoAnnualLeaveGrant(Base):
    __tablename__ = "auto_annual_leave_grant"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)

    account_based_january_1st = Column(
        Enum(
            "초기화", "다음해로 이월", name="account_january_1st"
        ),
        nullable=False,
        default="초기화",
        comment="매 년 1월 1일기준",
    )
    account_based_less_than_year = Column(
        Enum(
            "당해년도 일괄 부여", "매 월 1개씩 부여", name="account_less_than_year"
        ),
        nullable=False,
        default="당해년도 일괄 부여",
        comment="근속년수 1년 미만",
    )
    account_based_decimal_point = Column(
        Enum(
            "0.5 기준 올림", "절삭", "올림", "반올림", name="account_decimal_point"
        ),
        nullable=False,
        default="0.5 기준 올림",
        comment="소수점처리",
    )
    entry_date_based_remaining_leave = Column(
        Enum(
            "초기화", "다음해로 이월", name="entry_date_based"
        ),
        nullable=False,
        default="초기화",
        comment="매 년 입사일 기준",
    )
    condition_based_month = Column(Integer, nullable=False, default=0)
    condition_based_cnt = Column(Integer, nullable=False, default=0)
    condition_based_type = Column(
        Enum(
            "월", "일", name="condition_based_type"
        ),
        nullable=False,
        default="월",
    )

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

class AccountBasedGrantDto(BaseModel):
    account_based_january_1st: Literal['초기화', "다음해로 이월"] = Field(description="매 년 1월 1일기준", default="초기화")
    account_based_less_than_year: Literal['당해년도 일괄 부여', "매 월 1개씩 부여"] = Field(description="근속년수 1년 미만", default="당해년도 일괄 부여")
    account_based_decimal_point: Literal['0.5 기준 올림', "절삭", "올림", "반올림"] = Field(description="소수점처리", default="0.5 기준 올림")

    class Config:
        from_attributes = True

class EntryDateBasedGrantDto(BaseModel):
    entry_date_based_remaining_leave: Literal['초기화', "다음해로 이월"] = Field(description="매 년 입사일 기준", default="초기화")

    class Config:
        from_attributes = True

class ConditionBasedGrantDto(BaseModel):
    condition_based_month: int = Field(description="월", default=0)
    condition_based_cnt: int = Field(description="일", default=0)
    condition_based_type: Literal['월', "일"] = Field(description="월", default="월")

    class Config:
        from_attributes = True

class AutoAnnualLeaveGrantCombined(AccountBasedGrantDto, EntryDateBasedGrantDto, ConditionBasedGrantDto):
    pass