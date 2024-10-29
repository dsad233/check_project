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
    Numeric,
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from pydantic import BaseModel
from app.common.dto.pagination_dto import PaginationDto
from app.common.dto.search_dto import BaseSearchDto
from app.enums.users import StatusKor, Status

 

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
    decreased_days = Column(Numeric(10, 2), default=0.00)
    
    application_date = Column(Date, nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    approve_date = Column(Date, nullable=True)
    applicant_description = Column(String(255), nullable=True)
    admin_description = Column(String(255), nullable=True)
    
    status = Column(
        Enum(*[e.value for e in Status], name="leave_history_status"),
        nullable=False,
        default=Status.PENDING,
    )
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")
    
class LeaveHistoriesResponse(BaseModel):
    id: int
    branch_id: int
    branch_name: str
    user_id: int
    user_name: str
    part_id: int
    part_name: str
    
    application_date: datetime
    leave_category_name: str
    decreased_days: float
    
    status: str
    applicant_description: Optional[str]
    admin_description: Optional[str]
    approve_date: Optional[datetime]

class LeaveHistoriesCreate(BaseModel):
    leave_category_id: int
    date: datetime
    applicant_description: Optional[str]

class LeaveHistoriesUpdate(BaseModel):
    leave_category_id: int
    date: datetime
    applicant_description: Optional[str]

class LeaveHistoriesApprove(BaseModel):
    status: str
    admin_description: Optional[str]

class LeaveHistoriesSearchDto(BaseSearchDto):
    kind: Optional[str] = None
    status: Optional[str] = None
    
class LeaveHistoriesListResponse(BaseModel):
    list: list[LeaveHistoriesResponse]
    pagination: PaginationDto
