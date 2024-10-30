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
from enum import Enum as PyEnum
from app.enums.users import Weekday  # Weekday enum import 추가


# class WorkPolicies(Base):  # 근로기본 설정
#     __tablename__ = "work_policies"
#     # __table_args__ = (
#     #     Index('idx_part_policies_part_id', 'part_id')
#     # )
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
#     weekly_work_days = Column(Integer, nullable=False, default=5)  # 주 근무일수

#     # 월요일 설정
#     monday_start_time = Column(Time, nullable=False, default=time(9, 0))
#     monday_end_time = Column(Time, nullable=False, default=time(18, 0))
#     monday_is_holiday = Column(Boolean, default=False)

#     # 화요일 설정
#     tuesday_start_time = Column(Time, nullable=False, default=time(9, 0))
#     tuesday_end_time = Column(Time, nullable=False, default=time(18, 0))
#     tuesday_is_holiday = Column(Boolean, default=False)

#     # 수요일 설정
#     wednesday_start_time = Column(Time, nullable=False, default=time(9, 0))
#     wednesday_end_time = Column(Time, nullable=False, default=time(18, 0))
#     wednesday_is_holiday = Column(Boolean, default=False)

#     # 목요일 설정
#     thursday_start_time = Column(Time, nullable=False, default=time(9, 0))
#     thursday_end_time = Column(Time, nullable=False, default=time(18, 0))
#     thursday_is_holiday = Column(Boolean, default=False)

#     # 금요일 설정
#     friday_start_time = Column(Time, nullable=False, default=time(9, 0))
#     friday_end_time = Column(Time, nullable=False, default=time(18, 0))
#     friday_is_holiday = Column(Boolean, default=False)

#     # 토요일 설정
#     saturday_start_time = Column(Time, nullable=True, default=time(0, 0))
#     saturday_end_time = Column(Time, nullable=True, default=time(0, 0))
#     saturday_is_holiday = Column(Boolean, default=True)

#     # 일요일 설정
#     sunday_start_time = Column(Time, nullable=True, default=time(0, 0))
#     sunday_end_time = Column(Time, nullable=True, default=time(0, 0))
#     sunday_is_holiday = Column(Boolean, default=True)

#     # 의사 휴게시간
#     doctor_lunch_start_time = Column(Time, nullable=True, default=time(0, 0))
#     doctor_lunch_end_time = Column(Time, nullable=True, default=time(0, 0))
#     doctor_dinner_start_time = Column(Time, nullable=True, default=time(0, 0))
#     doctor_dinner_end_time = Column(Time, nullable=True, default=time(0, 0))

#     # 일반 직원 휴게시간
#     common_lunch_start_time = Column(Time, nullable=True, default=time(0, 0))
#     common_lunch_end_time = Column(Time, nullable=True, default=time(0, 0))
#     common_dinner_start_time = Column(Time, nullable=True, default=time(0, 0))
#     common_dinner_end_time = Column(Time, nullable=True, default=time(0, 0))

#     created_at = Column(DateTime, default=datetime.now)
#     updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
#     deleted_yn = Column(String(1), default="N")


# class WorkPoliciesDto(BaseModel):
#     weekly_work_days: int = Field(description="주 근무일수", default=5)

#     # 월요일 설정
#     monday_start_time: time = Field(description="월요일 시작 시간", default=time(9, 0))
#     monday_end_time: time = Field(description="월요일 종료 시간", default=time(18, 0))
#     monday_is_holiday: bool = Field(description="월요일 휴일 여부", default=False)

#     # 화요일 설정
#     tuesday_start_time: time = Field(description="화요일 시작 시간", default=time(9, 0))
#     tuesday_end_time: time = Field(description="화요일 종료 시간", default=time(18, 0))
#     tuesday_is_holiday: bool = Field(description="화요일 휴일 여부", default=False)

#     # 수요일 설정
#     wednesday_start_time: time = Field(description="수요일 시작 시간", default=time(9, 0))
#     wednesday_end_time: time = Field(description="수요일 종료 시간", default=time(18, 0))
#     wednesday_is_holiday: bool = Field(description="수요일 휴일 여부", default=False)

#     # 목요일 설정
#     thursday_start_time: time = Field(description="목요일 시작 시간", default=time(9, 0))
#     thursday_end_time: time = Field(description="목요일 종료 시간", default=time(18, 0))
#     thursday_is_holiday: bool = Field(description="목요일 휴일 여부", default=False)

#     # 금요일 설정
#     friday_start_time: time = Field(description="금요일 시작 시간", default=time(9, 0))
#     friday_end_time: time = Field(description="금요일 종료 시간", default=time(18, 0))
#     friday_is_holiday: bool = Field(description="금요일 휴일 여부", default=False)

#     # 토요일 설정
#     saturday_start_time: time = Field(description="토요일 시작 시간", default=time(0, 0))
#     saturday_end_time: time = Field(description="토요일 종료 시간", default=time(0, 0))
#     saturday_is_holiday: bool = Field(description="토요일 휴일 여부", default=True)

#     # 일요일 설정
#     sunday_start_time: time = Field(description="일요일 시작 시간", default=time(0, 0))
#     sunday_end_time: time = Field(description="일요일 종료 시간", default=time(0, 0))
#     sunday_is_holiday: bool = Field(description="일요일 휴일 여부", default=True)

#     # 의사 휴게시간
#     doctor_lunch_start_time: time = Field(description="의사 점심 휴게 시작 시간", default=time(0, 0))
#     doctor_lunch_end_time: time = Field(description="의사 점심 휴게 종료 시간", default=time(0, 0))
#     doctor_dinner_start_time: time = Field(description="의사 저녁 휴게 시작 시간", default=time(0, 0))
#     doctor_dinner_end_time: time = Field(description="의사 저녁 휴게 종료 시간", default=time(0, 0))

#     # 일반 직원 휴게시간
#     common_lunch_start_time: time = Field(description="일반 직원 점심 휴게 시작 시간", default=time(0, 0))
#     common_lunch_end_time: time = Field(description="일반 직원 점심 휴게 종료 시간", default=time(0, 0))
#     common_dinner_start_time: time = Field(description="일반 직원 저녁 휴게 시작 시간", default=time(0, 0))
#     common_dinner_end_time: time = Field(description="일반 직원 저녁 휴게 종료 시간", default=time(0, 0))

#     created_at: datetime = Field(description="생성일시")
#     updated_at: datetime = Field(description="수정일시")
#     deleted_yn: str = Field(description="삭제 여부")

#     class Config:
#         from_attributes = True


class WorkPolicies(Base):
    __tablename__ = "work_policies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    weekly_work_days = Column(Integer, nullable=False, default=5)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    work_schedules = relationship(
        "WorkSchedule", back_populates="work_policy", lazy="selectin"
    )
    break_times = relationship(
        "BreakTime", back_populates="work_policy", lazy="selectin"
    )


class WorkSchedule(Base):
    __tablename__ = "work_schedules"
    id = Column(Integer, primary_key=True, autoincrement=True)
    work_policy_id = Column(Integer, ForeignKey("work_policies.id"), nullable=False)
    day_of_week = Column(Enum(Weekday), nullable=False)
    start_time = Column(Time, nullable=False, default=time(9, 0))
    end_time = Column(Time, nullable=False, default=time(18, 0))
    is_holiday = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    work_policy = relationship("WorkPolicies", back_populates="work_schedules")


class BreakTime(Base):
    __tablename__ = "break_times"
    id = Column(Integer, primary_key=True, autoincrement=True)
    work_policy_id = Column(Integer, ForeignKey("work_policies.id"), nullable=False)
    is_doctor = Column(Boolean, default=False)
    break_type = Column(String(10), nullable=False)
    start_time = Column(Time, nullable=True, default=time(0, 0))
    end_time = Column(Time, nullable=True, default=time(0, 0))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    work_policy = relationship("WorkPolicies", back_populates="break_times")


# DTOs
class WorkScheduleDto(BaseModel):
    day_of_week: Weekday
    start_time: time
    end_time: time
    is_holiday: bool

    class Config:
        from_attributes = True
        use_enum_values = True


class BreakTimeDto(BaseModel):
    is_doctor: bool
    break_type: str
    start_time: time
    end_time: time

    class Config:
        from_attributes = True


class WorkPoliciesDto(BaseModel):
    id: int
    branch_id: int
    weekly_work_days: int
    work_schedules: list[WorkScheduleDto] = []
    break_times: list[BreakTimeDto] = []

    class Config:
        from_attributes = True
