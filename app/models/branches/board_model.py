from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum
from app.core.database import Base
from pydantic import BaseModel
from typing import Optional
from app.models.users.users_model import Users  # Users 모델 임포트

class Board(Base):
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)

    category_name = Column(String(255), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    
    read_authority = Column(
        Enum(
            "MSO 최고권한", "최고관리자", "관리자", "사원", "퇴사자", name="user_role"
        ),
        nullable=False,
        default="사원",
    )
    
    write_authority = Column(
        Enum(
            "MSO 최고권한", "최고관리자", "관리자", "사원", "퇴사자", name="user_role"
        ),
        nullable=False,
        default="사원",
    )
    
    notice_authority = Column(
        Enum(
            "MSO 최고권한", "최고관리자", "관리자", "사원", "퇴사자", name="user_role"
        ),
        nullable=False,
        default="관리자",
    )
    
    part_division = Column(Boolean, default=False)
    allow_comment = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

class BoardCreate(BaseModel):
    category_name: str
    description: Optional[str]
    
    read_authority: Optional[str]
    write_authority: Optional[str]
    notice_authority: Optional[str]
    
    part_division: Optional[bool]
    allow_comment: Optional[bool]

class BoardUpdate(BaseModel):
    category_name: Optional[str]
    division: Optional[bool]

class BoardResponse(BaseModel):
    id: int
    category_name: str
    description: str
    
    read_authority: str
    write_authority: str
    notice_authority: str
    
    part_division: bool
    allow_comment: bool


