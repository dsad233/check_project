from datetime import datetime
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
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from pydantic import BaseModel
from app.common.dto.pagination_dto import PaginationDto
from app.common.dto.search_dto import BaseSearchDto
class LeaveHistories(Base):
    __tablename__ = "leave_histories"
    __table_args__ = (
        Index("idx_leave_history_user_id", "user_id"),
        Index("idx_leave_history_application_date", "application_date"),
        UniqueConstraint("user_id", "application_date", name="uq_user_application_date"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    leave_category_id = Column(
        Integer, ForeignKey("leave_categories.id"), nullable=False
    )
    
    application_date = Column(Date, nullable=False)
    approve_date = Column(Date, nullable=True)
    applicant_description = Column(String(255), nullable=True)
    admin_description = Column(String(255), nullable=True)

    status = Column(
        Enum(
            "확인중", "승인", "반려", name="leave_history_status"
        ),
        nullable=False,
        default="확인중",
    )

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

class LeaveHistoriesCreate(BaseModel):
    leave_category_id: int
    date: datetime
    applicant_description: Optional[str]

class LeaveHistoriesResponse(BaseModel):
    id: int
    branch_name: str
    user_name: str
    part_name: str
    
    application_date: datetime
    leave_category_name: str
    
    status: str
    applicant_description: Optional[str]
    admin_description: Optional[str]
    approve_date: Optional[datetime]

class LeaveHistoriesSearchDto(BaseSearchDto):
    kind: Optional[str] = None
    status: Optional[str] = None
    
class LeaveHistoriesListResponse(BaseModel):
    list: list[LeaveHistoriesResponse]
    pagination: PaginationDto
