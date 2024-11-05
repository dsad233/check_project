from app.core.database import Base
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, DateTime
from datetime import datetime, UTC

from app.enums.users import GraduationType, SchoolType


class Education(Base):
    __tablename__ = 'educations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    school_type = Column(
        Enum(
            *[e.value for e in SchoolType],
            name="school_type"
        ),
        nullable=True
    )  # 학교 구분
    school_name = Column(String(255), nullable=True)  # 학교명
    graduation_type = Column(
        Enum(
            *[e.value for e in GraduationType],
            name="graduation_type"
        ),
        nullable=True
    )  # 졸업 구분
    major = Column(String(255), nullable=True)  # 전공
    admission_date = Column(Date, nullable=True)  # 입학일
    graduation_date = Column(Date, nullable=True)  # 졸업일

    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    deleted_yn = Column(String(1), default="N")