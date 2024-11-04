from app.core.database import Base
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, DateTime
from datetime import datetime, UTC


class Education(Base):
    __tablename__ = 'educations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    school_type = Column(Enum(SchoolType), nullable=False)  # 학교 구분
    school_name = Column(String(255), nullable=False)  # 학교명
    graduation_type = Column(Enum(GraduationType), nullable=False)  # 졸업 구분
    major = Column(String(255), nullable=True)  # 전공
    admission_date = Column(Date, nullable=False)  # 입학일
    graduation_date = Column(Date, nullable=True)  # 졸업일

    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    deleted_yn = Column(String(1), default="N")