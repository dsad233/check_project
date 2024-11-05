from datetime import datetime, time
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
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


class WorkPolicies(Base):
    __tablename__ = "work_policies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    weekly_work_days = Column(Integer, nullable=False, default=5)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    work_schedules = relationship(
        "BranchWorkSchedule", back_populates="work_policy", lazy="selectin"  # WorkSchedule -> BranchWorkSchedule
    )
    break_times = relationship(
        "BranchBreakTime", back_populates="work_policy", lazy="selectin"  # BreakTime -> BranchBreakTime
    ) 


class BranchWorkSchedule(Base):
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


class BranchBreakTime(Base):
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
