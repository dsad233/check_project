from datetime import datetime
from typing import Optional, List

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
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.common.dto.pagination_dto import PaginationDto
from app.core.database import Base


class LeaveCategory(Base):
    __tablename__ = "leave_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    name = Column(String(255), nullable=False)
    leave_count = Column(Integer, nullable=False)
    is_paid = Column(Boolean, nullable=False)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")


class LeaveCategoryDto(BaseModel):
    id: Optional[int] = Field(default=None, description="휴무 ID")
    name: str = Field(description="휴무 명")
    leave_count: int = Field(description="차감 일수")
    is_paid: bool = Field(description="유급 여부")

    class Config:
        from_attributes = True

