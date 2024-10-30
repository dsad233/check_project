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

