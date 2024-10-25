from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    Numeric
)
from sqlalchemy.orm import relationship

from app.core.database import Base

class UserLeavesDays(Base):
    __tablename__ = "user_leaves_days"
    __table_args__ = (
        Index("idx_user_leaves_days_user_id", "user_id"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    leave_category_id = Column(Integer, ForeignKey("leave_categories.id"), nullable=False)
    increased_days = Column(Numeric(10, 2), default=0.0)
    decreased_days = Column(Numeric(10, 2), default=0.0)
    description = Column(String(255), nullable=True)
    is_paid = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    total_leave_days = Column(Numeric(10, 2), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    user = relationship("Users", foreign_keys=[user_id], back_populates="leaves")
    approver = relationship("Users", foreign_keys=[approver_id], backref="approved_leaves")
    branch = relationship("Branches", foreign_keys=[branch_id], back_populates="user_leaves")
    
class UserLeavesDaysResponse(BaseModel):
    user_id: int = Field(..., gt=0) # 사용자 ID
    branch_id: int = Field(..., gt=0) # 지점 ID
    leave_category_id: int = Field(..., gt=0) # 휴무 카테고리 ID
    year: int = Field(..., gt=0) # 연도
    increased_days: float = Field(..., ge=0) # 증가 일수
    decreased_days: float = Field(..., ge=0) # 감소 일수