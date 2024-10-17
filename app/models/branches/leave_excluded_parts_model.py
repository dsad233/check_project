from datetime import datetime
from typing import List

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

class LeaveExcludedPart(Base):
    __tablename__ = "leave_excluded_parts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    leave_category_id = Column(Integer, ForeignKey("leave_categories.id"), nullable=False)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)

class LeaveExcludedPartResponse(BaseModel):
    id: int = Field(..., gt=0)
    leave_category_id: int = Field(..., gt=0)
    part_id: int = Field(..., gt=0)

    class Config:
        from_attributes = True

