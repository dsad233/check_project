from sqlalchemy import Column, Date, ForeignKey, Integer, Time, Enum
from app.core.database import Base
import enum

class WorkTypeEnum(enum.Enum):
    HOSPITAL = "병원"
    REMOTE = "재택"
    HOLIDAY = "휴일"

class PartTimerWorkContract(Base):
    __tablename__ = "part_timer_work_contracts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    contract_start_date = Column(Date, nullable=False)
    contract_end_date = Column(Date, nullable=False)

class PartTimerWorkingTime(Base):
    __tablename__ = "part_timer_working_times"

    id = Column(Integer, primary_key=True, autoincrement=True)
    part_timer_work_contract_id = Column(Integer, ForeignKey("part_timer_work_contracts.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False) # 0: 일요일, 1: 월요일, 2: 화요일, 3: 수요일, 4: 목요일, 5: 금요일, 6: 토요일
    work_start_time = Column(Time, nullable=False)
    work_end_time = Column(Time, nullable=False)

class PartTimerHourlyWage(Base):
    __tablename__ = "part_timer_hourly_wages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    part_timer_work_contract_id = Column(Integer, ForeignKey("part_timer_work_contracts.id"), nullable=False)
    calculate_start_time = Column(Time, nullable=False)
    calculate_end_time = Column(Time, nullable=False)
    hourly_wage = Column(Integer, nullable=False)

'''
출퇴근 기록 별로 추가 정보
'''
class PartTimerAdditionalInfo(Base):
    __tablename__ = "part_timer_additional_infos"

    commute_id = Column(Integer, ForeignKey("commutes.id"), primary_key=True, nullable=False)
    work_type = Column(Enum(WorkTypeEnum), nullable=False)
    rest_minutes = Column(Integer, nullable=False, default=30)
    work_set_start_time = Column(Time, nullable=False)
    work_set_end_time = Column(Time, nullable=False)