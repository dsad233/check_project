from datetime import datetime, UTC
from sqlalchemy import Column, Enum, Integer, ForeignKey, Date, Time, Boolean, DateTime, String
from app.core.database import Base
from app.enums.users import Weekday

class WorkContract(Base):
    __tablename__ = "work_contract"
    """
    근로계약서
    """

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # 계약일
    contract_creation_date = Column(Date, nullable=False, default=datetime.now(UTC)) # 계약서 작성일
    contract_start_date = Column(Date, nullable=False) # 계약 시작일
    contract_end_date = Column(Date, nullable=True) # 계약 종료일
    is_fixed_rest_day = Column(Boolean, nullable=False, default=False)

    #근로 기본 설정
    weekly_work_start_time = Column(Time, nullable=False)
    weekly_work_end_time = Column(Time, nullable=False)
    saturday_work_start_time = Column(Time, nullable=True)
    saturday_work_end_time = Column(Time, nullable=True)
    sunday_work_start_time = Column(Time, nullable=True)
    sunday_work_end_time = Column(Time, nullable=True)

    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    deleted_yn = Column(Boolean, default="N")



class FixedRestDay(Base):
    __tablename__ = "fixed_rest_day"
    """
    고정 휴무일
    """

    id = Column(Integer, primary_key=True, autoincrement=True)
    work_contract_id = Column(Integer, ForeignKey("work_contract.id"), nullable=False)

    rest_day = Column(Enum(Weekday, name="weekday"), nullable=False)
    every_over_week = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))



class WorkContractBreakTime(Base):
    __tablename__ = "work_contract_break_time"
    """
    근로계약서 내 휴게시간
    """

    id = Column(Integer, primary_key=True, autoincrement=True)
    work_contract_id = Column(Integer, ForeignKey("work_contract.id"), nullable=False)

    break_start_time = Column(Time, nullable=False)
    break_end_time = Column(Time, nullable=False)

    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    deleted_yn = Column(String(1), default="N")
