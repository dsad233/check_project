from datetime import datetime
from pydantic import field_validator, Field
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship
from app.core.database import Base
from fastapi import HTTPException
from pydantic_settings import BaseSettings


class OverTimePolicies(Base):  # 연장근무 설정
    __tablename__ = "overtime_policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    name = Column(String(255), nullable=False)  # 예: 의사, 간호사...
    
    # 연장근무 당 지급 금액 설정
    ot_30 = Column(Integer, nullable=False)
    ot_60 = Column(Integer, nullable=False)
    ot_90 = Column(Integer, nullable=False)
    ot_120 = Column(Integer, nullable=False)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")


class OverTimeUpdate(BaseSettings):
    name: str = Field(description="파트명")
    ot_30: int = Field(description="O.T 30분 초과")
    ot_60: int = Field(description="O.T 60분 초과")
    ot_90: int = Field(description="O.T 90분 초과")
    ot_120: int = Field(description="O.T 120분 초과")

    @field_validator("ot_30")
    @classmethod
    def check_ot_30(cls, ot_30):
        if ot_30 is None:
            raise HTTPException(status_code=400, detail="ot_30란이 누락되었습니다. 다시 작성해주세요.")
        return ot_30

    @field_validator("ot_60")
    @classmethod
    def check_ot_60(cls, ot_60):
        if ot_60 is None:
            raise HTTPException(status_code=400, detail="ot_60란이 누락되었습니다. 다시 작성해주세요.")
        return ot_60

    @field_validator("ot_90")
    @classmethod
    def check_ot_90(cls, ot_90):
        if ot_90 is None:
            raise HTTPException(status_code=400, detail="ot_90란이 누락되었습니다. 다시 작성해주세요.")
        return ot_90

    @field_validator("ot_120")
    @classmethod
    def check_ot_120(cls, ot_120):
        if ot_120 is None:
            raise HTTPException(status_code=400, detail="ot_120란이 누락되었습니다. 다시 작성해주세요.")
        return ot_120


class OverTimeCreate(BaseSettings):
    name: str = Field(description="파트명")
    ot_30: int = Field(description="O.T 30분 초과")
    ot_60: int = Field(description="O.T 60분 초과")
    ot_90: int = Field(description="O.T 90분 초과")
    ot_120: int = Field(description="O.T 120분 초과")

    @field_validator("ot_30")
    @classmethod
    def check_ot_30(cls, ot_30):
        if ot_30 is None:
            raise HTTPException(status_code=400, detail="ot_30란이 누락되었습니다. 다시 작성해주세요.")
        return ot_30

    @field_validator("ot_60")
    @classmethod
    def check_ot_60(cls, ot_60):
        if ot_60 is None:
            raise HTTPException(status_code=400, detail="ot_60란이 누락되었습니다. 다시 작성해주세요.")
        return ot_60

    @field_validator("ot_90")
    @classmethod
    def check_ot_90(cls, ot_90):
        if ot_90 is None:
            raise HTTPException(status_code=400, detail="ot_90란이 누락되었습니다. 다시 작성해주세요.")
        return ot_90

    @field_validator("ot_120")
    @classmethod
    def check_ot_120(cls, ot_120):
        if ot_120 is None:
            raise HTTPException(status_code=400, detail="ot_120란이 누락되었습니다. 다시 작성해주세요.")
        return ot_120
