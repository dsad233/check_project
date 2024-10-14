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


class LeaveCategories(Base):
    __tablename__ = "leave_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    name = Column(String(255), nullable=False)
    leave_count = Column(Integer, nullable=False)
    is_paid = Column(Boolean, nullable=False)
    is_leave_of_absence = Column(Boolean, default=False)  # 휴직 여부

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")


class LeaveCreate(BaseModel):
    name: str = Field(description="휴무 명")
    leave_count: int = Field(description="차감 일수")
    is_paid: bool = Field(description="유급 여부")
    is_leave_of_absence: bool = Field(description="휴직 여부")


class LeaveResponse(BaseModel):
    id: int = Field(description="휴무 ID")
    branch_id: int = Field(description="지점 ID")
    name: str = Field(description="휴무 명")
    leave_count: int = Field(description="차감 일수")
    is_paid: bool = Field(description="유급 여부")
    is_leave_of_absence: bool = Field(description="휴직 여부")
    created_at: datetime = Field(description="생성 일시")
    updated_at: datetime = Field(description="수정 일시")
    deleted_yn: str = Field(description="삭제 여부")

    class Config:
        from_attributes = True


class LeaveListResponse(BaseModel):
    list: List[LeaveResponse] = Field(description="휴무 목록")
    pagination: PaginationDto = Field(description="페이지네이션")
