from datetime import datetime, time
from pydantic import BaseModel, Field
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

from app.core.database import Base

class MinimumWagePolicy(Base):
    __tablename__ = "minimum_wage_policies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    minimum_wage = Column(Integer, nullable=False)
    person_in_charge = Column(String(255), nullable=False) # 담당자
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

class MinimumWagePolicyDto(BaseModel):
    minimum_wage: int = Field(description="최저시급")
    # 업데이트일 추가하기
    person_in_charge: str = Field(description="담당자")

    class Config:
        from_attributes = True