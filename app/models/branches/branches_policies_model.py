
from datetime import datetime

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

# 해당 지점 권한 policies는 MSO, 최고관리자 한정이니, 다른 관리자급에 대해서는 고민할 필요 없음.
class BranchPolicies(Base): # 지점 설정 전체를 아우르는 테이블
    __tablename__ = "branch_policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)

    # 지점에 대한 정보
    branch_code = Column(String(50), nullable=False, unique=True)
    representative_doctor = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False)
    branch_name = Column(String(100), nullable=False)
    business_number = Column(String(20), nullable=False)
    address = Column(String(255), nullable=False)
    email = Column(String(100), nullable=False)
    
    # 이미지 파일 경로를 저장하는 필드들
    seal_image_path = Column(String(255), nullable=True)
    nameplate_image_path = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")
