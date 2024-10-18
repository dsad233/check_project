from pydantic import BaseModel
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from app.core.database import Base
from pydantic_settings import BaseSettings
from enum import Enum


class Attendance(Base):
    __tablename__ = "attendance"


    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    part_id = Column(Integer, ForeignKey('parts.id'), nullable=False)
    branch_name = Column(String(20), nullable=False)
    name = Column(String(10),nullable=False)
    gender = Column(String(5), nullable= False)
    part_name = Column(String(255), nullable=False)

    # 근무 일자
    workdays = Column(Integer, default=0)
    # 휴직 일자
    leavedays = Column(Integer, default=0)
    # 정규 휴무
    regular_holiday = Column(Integer, default=0)
    # 연차 사용
    annual_leave = Column(Integer, default=0)
    # 무급 사용
    unpaid_use = Column(Integer, default=0)

    # 재택 근무
    work_from_home = Column(Integer, default=0)
    # 주말 근무 시간
    weekend_work_hours = Column()
    # 주말 근무 수당
    holiday_work = Column(Integer, default=0)

    # O.T 30분 횟수
    ot_30 = Column(Integer, default= 0)
    # O.T 60분 횟수
    ot_60 = Column(Integer, default= 0)
    # O.T 90분 횟수
    ot_90 = Column(Integer, default= 0)
    # O.T 총 금액
    ot_total = Column(Integer, default= 0)

class UserEnum(str, Enum):
    male = "남자"
    femail = "여자"
    
class AttendanceCreate(BaseSettings):
    branch_name : str
    name : str
    gender : UserEnum
    part_name : str
    # 근무 일자
    workdays : int
    # 휴직 일자
    leavedays : int
    # 정규 휴무
    regular_holiday : int
    # 연차 사용
    annual_leave : int
    # 무급 사용
    unpaid_use : int
    
    # 재택 근무
    work_from_home : int 
    # 주말 근무 시간
    weekend_work_hours : int
    # 주말 근무 수당
    holiday_work : int

    # O.T 30분 횟수
    ot_30 : int
    # O.T 60분 횟수
    ot_60 : int
    # O.T 90분 횟수
    ot_90 = int
    # O.T 총 금액 
    # ot_total : 

    parts = relationship("Attendance", back_populates="parts")
    branchs = relationship("Attendance", back_populates="branchs")
    


 


    attendance = relationship("Branches", back_populates="attendance")
    attendance = relationship("Parts", back_populates="attendance")