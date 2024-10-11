from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Users(Base):
    
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    role = Column(Enum('MSO 최고권한', '최고관리자', '관리자', '사원', name='user_role'), nullable=True, default='사원')
    part = Column(Enum('외래팀', '관리', '의사', '총괄 상담실장', '간호조무사', '코디네이터', '피부관리자', '상담실장', name='user_part'), nullable=True)
    created_at = Column(DateTime, nullable=True, default=datetime.now)
    updated_at = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), nullable=True)
    commutes = relationship("Commute", back_populates="user")
    personnel_records = relationship("PersonnelRecord", foreign_keys="PersonnelRecord.user_id",  back_populates="user")
    annual_leaves_proposer = relationship("AnnualLeave", foreign_keys="AnnualLeave.proposer_id", back_populates="proposer")
    annual_leaves_manager = relationship("AnnualLeave", foreign_keys="AnnualLeave.manager_id", back_populates="manager")
    overtimes_proposer = relationship("Overtime", foreign_keys="Overtime.proposer_id", back_populates="proposer")
    overtimes_manager = relationship("Overtime", foreign_keys="Overtime.manager_id", back_populates="manager")


class Commute(Base):
    
    __tablename__ = "commutes"

    commute_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    work_time = Column(Integer, nullable=True)
    updated_at = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), nullable=True)
    user = relationship("Users", back_populates="commutes")


class PersonnelRecord(Base):
    __tablename__ = "personnel_records"
    personnel_record_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    manager_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    category = Column(Enum('평가', '경고', '감사', '감봉', '해고', name='record_category'), nullable=True)
    created_at = Column(DateTime, nullable=True, default=datetime.now)
    updated_at = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), nullable=True)
    user = relationship("Users", foreign_keys=[user_id], back_populates="personnel_records")
    manager = relationship("Users", foreign_keys=[manager_id])
    

class AnnualLeave(Base):
    
    __tablename__ = "annual_leaves"

    annual_leave_id = Column(Integer, primary_key=True)
    manager_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    proposer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    application_date = Column(DateTime, nullable=True)
    type = Column(Enum('annual_leave', 'sick_leave', 'bereavement_leave', 'parental_leave', 'leave_of_absence', 'official_leave', name='leave_type'), nullable=True)
    date_count = Column(Integer, nullable=True)
    application_status = Column(Enum('pending', 'approved', 'rejected', name='application_status'), nullable=True, default='pending')
    proposer_note = Column(Text, nullable=True)
    manager_note = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True, default=datetime.now)
    updated_at = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), nullable=True, default='N')
    proposer = relationship("Users", foreign_keys=[proposer_id], back_populates="annual_leaves_proposer")
    manager = relationship("Users", foreign_keys=[manager_id], back_populates="annual_leaves_manager")


class Overtime(Base):
    
    __tablename__ = "overtimes"

    overtime_id = Column(Integer, primary_key=True)
    manager_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    proposer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    application_date = Column(DateTime, nullable=True)
    overtime = Column(Enum('30', '60', '90', '120', name='overtime_duration'), nullable=True, default='30')
    application_note = Column(Text, nullable=True)
    proposer_note = Column(Text, nullable=True)
    processed_date = Column(DateTime, nullable=True)
    application_status = Column(Enum('pending', 'approved', 'rejected', name='application_status'), nullable=True, default='pending')
    created_at = Column(DateTime, nullable=True, default=datetime.now)
    updated_at = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), nullable=True)
    proposer = relationship("Users", foreign_keys=[proposer_id], back_populates="overtimes_proposer")
    manager = relationship("Users", foreign_keys=[manager_id], back_populates="overtimes_manager")