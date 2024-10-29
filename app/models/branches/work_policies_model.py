from datetime import datetime, time
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
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    weekly_work_days = Column(Integer, nullable=False, default=5)  # 주 근무일수

    # 평일 설정
    weekday_start_time = Column(Time, nullable=False, default=time(9, 0))
    weekday_end_time = Column(Time, nullable=False, default=time(18, 0))
    weekday_is_holiday = Column(Boolean, default=False)

    # 토요일 설정
    saturday_start_time = Column(Time, nullable=True, default=time(0, 0))
    saturday_end_time = Column(Time, nullable=True, default=time(0, 0))
    saturday_is_holiday = Column(Boolean, default=True)

    # 일요일 설정
    sunday_start_time = Column(Time, nullable=True, default=time(0, 0))
    sunday_end_time = Column(Time, nullable=True, default=time(0, 0))
    sunday_is_holiday = Column(Boolean, default=True)

    # 의사 휴게시간
    doctor_lunch_start_time = Column(Time, nullable=True, default=time(0, 0))
    doctor_lunch_end_time = Column(Time, nullable=True, default=time(0, 0))
    doctor_dinner_start_time = Column(Time, nullable=True, default=time(0, 0))
    doctor_dinner_end_time = Column(Time, nullable=True, default=time(0, 0))

    # 일반 직원 휴게시간
    common_lunch_start_time = Column(Time, nullable=True, default=time(0, 0))
    common_lunch_end_time = Column(Time, nullable=True, default=time(0, 0))
    common_dinner_start_time = Column(Time, nullable=True, default=time(0, 0))
    common_dinner_end_time = Column(Time, nullable=True, default=time(0, 0))

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")


class WorkPoliciesDto(BaseModel):
    weekly_work_days: int = Field(description="주 근무일수", default=5)
    weekday_start_time: time = Field(description="평일 시작 시간", default=time(9, 0))
    weekday_end_time: time = Field(description="평일 종료 시간", default=time(18, 0))
    weekday_is_holiday: bool = Field(description="평일 휴일 여부", default=False)
    saturday_start_time: time = Field(description="토요일 시작 시간", default=time(0, 0))
    saturday_end_time: time = Field(description="토요일 종료 시간", default=time(0, 0))
    saturday_is_holiday: bool = Field(description="토요일 휴일 여부", default=True)
    sunday_start_time: time = Field(description="일요일 시작 시간", default=time(0, 0))
    sunday_end_time: time = Field(description="일요일 종료 시간", default=time(0, 0))
    sunday_is_holiday: bool = Field(description="일요일 휴일 여부", default=True)
    doctor_lunch_start_time: time = Field(description="의사 휴게 시작 시간", default=time(0, 0))
    doctor_lunch_end_time: time = Field(description="의사 휴게 종료 시간", default=time(0, 0))
    doctor_dinner_start_time: time = Field(description="의사 휴게 시작 시간", default=time(0, 0))
    doctor_dinner_end_time: time = Field(description="의사 휴게 종료 시간", default=time(0, 0))
    common_lunch_start_time: time = Field(description="일반 직원 휴게 시작 시간", default=time(0, 0))
    common_lunch_end_time: time = Field(description="일반 직원 휴게 종료 시간", default=time(0, 0))
    common_dinner_start_time: time = Field(description="일반 직원 휴게 시작 시간", default=time(0, 0))
    common_dinner_end_time: time = Field(description="일반 직원 휴게 종료 시간", default=time(0, 0))


    class Config:
        from_attributes = True