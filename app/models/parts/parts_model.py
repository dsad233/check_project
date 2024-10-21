from datetime import datetime
from typing import Optional

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
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class Parts(Base):
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    name = Column(String(255), nullable=False)
    task = Column(String(500), nullable=True)
    color = Column(String(255), nullable=True)
    is_doctor = Column(Boolean, default=False)
    required_certification = Column(Boolean, default=False)
    leave_granting_authority = Column(Boolean, default=False)

    auto_annual_leave_grant = Column(
        Enum(
            "수동부여", "회계기준 부여", "입사일 기준 부여", "조건별 부여", name="part_auto_annual_leave_grant"
        ),
        nullable=False,
        default="수동부여",
    )

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(
        String(1), default="N"
    )  # annual_leaves = relationship("AnnualLeave", back_populates="part")



class PartCreate(BaseModel):
    name: str = Field(..., min_length=1, description="파트 이름")
    task: str = Field(..., min_length=1, description="파트 업무")
    color: str = Field(..., min_length=1, description="파트 색상")
    is_doctor: bool
    required_certification: bool


class PartUpdate(BaseModel):
    name: Optional[str] = None
    task: Optional[str] = None
    color: Optional[str] = None
    is_doctor: Optional[bool] = None
    required_certification: Optional[bool] = None


class PartResponse(BaseModel):
    id: int
    name: str
    task: Optional[str] = None
    color: Optional[str] = None
    is_doctor: bool
    required_certification: bool
    leave_granting_authority: bool
    
    class Config:
        from_attributes = True