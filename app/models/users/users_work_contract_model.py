from datetime import datetime, UTC
from sqlalchemy import Column, Enum, Integer, ForeignKey, Date, Time, Boolean, DateTime
from app.core.database import Base
from app.enums.users import Weekday

class WorkContract(Base):
    __tablename__ = "work_contract"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # 계약일
    contract_start_date = Column(Date, nullable=False)
    contract_end_date = Column(Date, nullable=True)
    is_fixed_rest_day = Column(Boolean, nullable=False, default=False)

    #근로 기본 설정
    weekly_work_start_time = Column(Time, nullable=False)
    weekly_work_end_time = Column(Time, nullable=False)
    weekly_is_rest = Column(Boolean, nullable=False, default=False)
    saturday_work_start_time = Column(Time, nullable=True)
    saturday_work_end_time = Column(Time, nullable=True)
    saturday_is_rest = Column(Boolean, nullable=False, default=True)
    sunday_work_start_time = Column(Time, nullable=True)
    sunday_work_end_time = Column(Time, nullable=True)
    sunday_is_rest = Column(Boolean, nullable=False, default=True)

    # 휴게시간
    break_start_time = Column(Time, nullable=True)
    break_end_time = Column(Time, nullable=True)
    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

class FixedRestDay(Base):
    __tablename__ = "fixed_rest_day"
    id = Column(Integer, primary_key=True, autoincrement=True)
    work_contract_id = Column(Integer, ForeignKey("work_contract.id"), nullable=False)
    rest_day = Column(Enum(Weekday, name="weekday"), nullable=False)
    every_over_week = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))