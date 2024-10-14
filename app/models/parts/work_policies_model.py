from datetime import datetime

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
    Time,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class WorkPolicies(Base):  # 근로기본 설정
    __tablename__ = "work_policies"
    # __table_args__ = (
    #     Index('idx_part_policies_part_id', 'part_id')
    # )
    id = Column(Integer, primary_key=True, autoincrement=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    weekly_work_days = Column(Integer, nullable=False)  # 주 근무일수

    # 평일 설정
    weekday_start_time = Column(Time, nullable=False)
    weekday_end_time = Column(Time, nullable=False)
    weekday_is_holiday = Column(Boolean, default=False)

    # 토요일 설정
    saturday_start_time = Column(Time, nullable=True)
    saturday_end_time = Column(Time, nullable=True)
    saturday_is_holiday = Column(Boolean, default=True)

    # 일요일 설정
    sunday_start_time = Column(Time, nullable=True)
    sunday_end_time = Column(Time, nullable=True)
    sunday_is_holiday = Column(Boolean, default=True)

    # 의사 휴게시간
    doctor_break_start_time = Column(Time, nullable=True)
    doctor_break_end_time = Column(Time, nullable=True)

    # 일반 직원 휴게시간
    staff_break_start_time = Column(Time, nullable=True)
    staff_break_end_time = Column(Time, nullable=True)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")
