from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from app.core.database import Base
from datetime import date, datetime
from typing import Dict, Optional, List
from pydantic import BaseModel, Field, field_validator

class ClosedDays(Base):
    __tablename__ = "closed_days"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=True, index=True)
    part_id = Column(Integer, ForeignKey('parts.id'), nullable=True)
    user_id = Column(Integer,ForeignKey('users.id'), nullable=True)
    closed_day_date = Column(Date, nullable=False, index=True)
    memo = Column(String(500))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")


class BranchClosedDay(BaseModel):
    hospital_closed_days: List[date]
    
    @field_validator("hospital_closed_days")
    @classmethod
    def validate_date(cls, dates: List[date]) -> List[date]:
        today = date.today()
        for d in dates:
            if d < today:
                raise ValueError("휴무일 등록과 삭제는 오늘 이후의 날짜여야 합니다.")
        return dates

    # @field_validator("memo")
    # @classmethod
    # def validate_memo(cls, v):
    #     if v is not None and len(v.strip()) == 0:
    #         raise ValueError("메모는 비어있을 수 없습니다.")
    #     return v
    
    model_config = {
        "from_attributes": True
    }

class UserClosedDays(BaseModel):
    user_closed_days: Dict[int, List[date]]
    
    @field_validator("user_closed_days")
    @classmethod
    def validate_dates(cls, user_dates: Dict[int, List[date]]) -> Dict[int, List[date]]:
        today = date.today()
        for user_id, dates in user_dates.items():
            for d in dates:
                if d < today:
                    raise ValueError(f"사용자 ID {user_id}의 휴무일 등록과 삭제는 오늘 이후의 날짜여야 합니다.")
        return user_dates
    
    model_config = {
        "from_attributes": True
    }
    
class EarlyClockIn(Base):
    __tablename__ = "early_clock_in"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer,ForeignKey('users.id'), nullable=True)
    branch_id = Column(Integer,ForeignKey('branches.id'), nullable=True)
    early_clock_in = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

class UserEarlyClockIn(BaseModel):
    early_clock_in_users: Dict[int, List[datetime]]
    
    @field_validator("early_clock_in_users")
    @classmethod
    def validate_time(cls, early_clock_in_users: Dict[int, List[datetime]]) -> Dict[int, List[datetime]]:
        for user_id, times in early_clock_in_users.items():
            for time in times:
                # 시간을 9:00 ~ 10:40 사이로 제한
                if time.time() < datetime.strptime("09:00", "%H:%M").time() or \
                   time.time() > datetime.strptime("10:40", "%H:%M").time():
                    raise ValueError(f"조기 출근 시간은 09:00 ~ 10:40 사이여야 합니다. (입력된 시간: {time.strftime('%H:%M')})")
        return early_clock_in_users
    
    model_config = {
        "from_attributes": True
    }