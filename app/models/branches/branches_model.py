from datetime import datetime
from typing import List 
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Index
)
from sqlalchemy.orm import relationship
from app.core.database import Base
from pydantic import BaseModel, Field, field_validator
from app.common.dto.pagination_dto import PaginationDto


class Branches(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    representative_name = Column(String(255), nullable=False)
    registration_number = Column(String(255), nullable=False)
    call_number = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    corporate_seal = Column(String(255), nullable=False)
    nameplate = Column(String(255), nullable=False)
    mail_address = Column(String(255), nullable=False)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")


class BranchCreate(BaseModel):
    code: str = Field(description="지점 코드")
    name: str = Field(description="지점 이름")
    representative_name: str = Field(description="대표 원장 이름")
    registration_number: str = Field(description="사업자번호")
    call_number: str = Field(description="전화번호")
    address: str = Field(description="지점 주소")
    corporate_seal: str = Field(description="법인 도장")
    nameplate: str = Field(description="명판")
    mail_address: str = Field(description="메일 주소")

class BranchResponse(BaseModel):
    id: int = Field(description="지점 아이디")
    code: str = Field(description="지점 코드")
    name: str = Field(description="지점 이름")
    representative_name: str = Field(description="대표 원장 이름")
    registration_number: str = Field(description="사업자번호")
    call_number: str = Field(description="전화번호")
    address: str = Field(description="지점 주소")
    corporate_seal: str = Field(description="법인 도장")
    nameplate: str = Field(description="명판")
    mail_address: str = Field(description="메일 주소")
    created_at: datetime = Field(description="생성 일자")
    updated_at: datetime = Field(description="수정 일자")
    deleted_yn: str = Field(description="삭제 여부")

    class Config:
        from_attributes = True

class BranchListResponse(BaseModel):
    list: List[BranchResponse] = Field(description="지점 목록")
    pagination: PaginationDto = Field(description="페이지네이션")

class BranchDelete(BaseModel):
    id: int = Field(description="지점 아이디")