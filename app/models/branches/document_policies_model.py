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

# 문서 설정 관련 테이블 #
class DocumentPolicies(Base):
    __tablename__ = "document_policies"
    # __table_args__ = (
    #     Index('idx_part_policies_branch_id', 'branch_id'),
    #     Index('idx_part_policies_branch_policy_id', 'branch_policy_id'),
    # )
    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    document_type = Column(String(255), nullable=False)
    can_view = Column(Boolean, default=False)
    can_edit = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")