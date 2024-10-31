from datetime import datetime

from fastapi import HTTPException
from pydantic import Field, field_validator, BaseModel
from pydantic_settings import BaseSettings
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class OverTimePolicies(Base):  # 연장근무 설정
    __tablename__ = "overtime_policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)

    # 연장근무 당 지급 금액 설정
    doctor_ot_30 = Column(Integer, nullable=False, default=0)
    doctor_ot_60 = Column(Integer, nullable=False, default=0)
    doctor_ot_90 = Column(Integer, nullable=False, default=0)
    doctor_ot_120 = Column(Integer, nullable=False, default=0)

    common_ot_30 = Column(Integer, nullable=False, default=0)
    common_ot_60 = Column(Integer, nullable=False, default=0)
    common_ot_90 = Column(Integer, nullable=False, default=0)
    common_ot_120 = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

