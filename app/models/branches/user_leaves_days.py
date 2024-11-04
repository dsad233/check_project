from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Numeric
)

from app.core.database import Base

class UserLeavesDays(Base):
    __tablename__ = "user_leaves_days"
    __table_args__ = (
        Index("idx_user_leaves_days_user_id", "user_id"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)  # 고유 식별자
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 사용자 ID
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)  # 파트 ID
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)  # 지점 ID
    increased_days = Column(Numeric(10, 2), default=0.00, nullable=False)  # 증가된 휴가 일수
    decreased_days = Column(Numeric(10, 2), default=0.00, nullable=False)  # 감소된 휴가 일수
    total_leave_days = Column(Numeric(10, 2), default=0.00, nullable=False)  # 총 휴가 일수
    created_at = Column(DateTime, default=datetime.now)  # 생성 일시
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 수정 일시
    deleted_yn = Column(String(1), default="N")  # 삭제 여부 (Y/N)

    
    
class UserLeavesDaysResponse(BaseModel):
    user_id: int = Field(..., gt=0) # 사용자 ID
    branch_id: int = Field(..., gt=0) # 지점 ID
    increased_days: Optional[float] = Field(default=0.00, ge=0) # 증가 일수
    decreased_days: Optional[float] = Field(default=0.00, ge=0) # 감소 일수
    total_leave_days: Optional[float] = Field(default=0.00, ge=0) # 총 휴무 일수
    year: Optional[int] = Field(None, gt=0) # 연도
    
class UserLeaveInfo(BaseModel):
    """사용자 연차 정보를 담는 모델"""
    user_id: int
    branch_id: int
    year: Optional[int]
    increased_days: Optional[float]
    decreased_days: Optional[float]
    total_leave_days: Optional[float]
    message: Optional[str] = None