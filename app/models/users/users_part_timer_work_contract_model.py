from sqlalchemy import Column, Date, ForeignKey, Integer, Time
from app.core.database import Base


class PartTimerWorkContract(Base):
    __tablename__ = "part_timer_work_contract"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    contract_start_date = Column(Date, nullable=False)
    contract_end_date = Column(Date, nullable=False)
    weekly_work_days = Column(Integer, nullable=False)
    rest_minutes = Column(Integer, nullable=False)


class PartTimerWorkingTime(Base):
    __tablename__ = "part_timer_working_time"

    id = Column(Integer, primary_key=True, autoincrement=True)
    part_timer_work_contract_id = Column(Integer, ForeignKey("part_timer_work_contract.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False) # 0: 일요일, 1: 월요일, 2: 화요일, 3: 수요일, 4: 목요일, 5: 금요일, 6: 토요일
    work_start_time = Column(Time, nullable=False)
    work_end_time = Column(Time, nullable=False)

class PartTimerHourlyWage(Base):
    __tablename__ = "part_timer_hourly_wage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    part_timer_work_contract_id = Column(Integer, ForeignKey("part_timer_work_contract.id"), nullable=False)
    calculate_start_time = Column(Time, nullable=False)
    calculate_end_time = Column(Time, nullable=False)
    hourly_wage = Column(Integer, nullable=False)


    

 