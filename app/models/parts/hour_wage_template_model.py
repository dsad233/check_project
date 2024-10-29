from datetime import datetime, time
from pydantic import BaseModel, Field, field_validator
from typing import Optional
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


class HourWageTemplate(Base):
    __tablename__ = "hour_wage_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=True)
    name = Column(String(255), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    hour_wage = Column(Integer, nullable=False)
    home_hour_wage = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

class HourWageTemplateCreate(BaseModel):
    part_id: Optional[int] = Field(description="직책 ID")
    name: str = Field(description="템플릿 명")
    start_time: time = Field(description="시작 시간")
    end_time: time = Field(description="종료 시간")
    hour_wage: int = Field(description="시급")
    home_hour_wage: int = Field(description="재택근무시급 시급")

    @field_validator('part_id', mode='before')
    @classmethod
    def set_part_id(cls, v):
        return None if v == 0 else v

class HourWageTemplateUpdate(BaseModel):
    part_id: Optional[int] = Field(description="직책 ID")
    name: str = Field(description="템플릿 명")
    start_time: time = Field(description="시작 시간")
    end_time: time = Field(description="종료 시간")
    hour_wage: int = Field(description="시급")
    home_hour_wage: int = Field(description="재택근무시급 시급")

    @field_validator('part_id', mode='before')
    @classmethod
    def set_part_id(cls, v):
        return None if v == 0 else v

class HourWageTemplateResponse(BaseModel):
    id: int = Field(description="아이디")
    part_id: Optional[int] = Field(default=0, description="직책 ID")
    name: str = Field(description="템플릿 명")
    start_time: time = Field(description="시작 시간")
    end_time: time = Field(description="종료 시간")
    hour_wage: int = Field(description="시급")
    home_hour_wage: int = Field(description="재택근무시급 시급")

    @field_validator('part_id', mode='before')
    @classmethod
    def set_part_id(cls, v):
        return 0 if v is None else v

    class Config:
        from_attributes = True

