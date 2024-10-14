from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from app.core.database import Base


class HumanRecordCategory(Base):
    __tablename__ = "human_record_category"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)

    category_name = Column(String(255), unique=True, nullable=False)
    division = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")


class HumanRecordCategoryCreate(BaseModel):
    category_name: str
    division: bool


class HumanRecordCategoryUpdate(BaseModel):
    category_name: Optional[str]
    division: Optional[bool]


class HumanRecordCategoryResponse(BaseModel):
    id: int
    category_name: str
    division: bool
