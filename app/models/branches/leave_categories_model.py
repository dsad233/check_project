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
    Index,
    UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class LeaveCategories(Base):
    __tablename__ = "leave_categories"
    __table_args__ = (
        Index('idx_leave_category_branch_id', 'branch_id'),
        Index('idx_leave_category_date', 'date'),
        UniqueConstraint('branch_id', 'date', name='uq_branch_date'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    date = Column(Date, nullable=False)
    is_paid = Column(Boolean, nullable=False)
    description = Column(String(255), nullable=True)
    leave_count = Column(Integer, nullable=False)
    is_leave_of_absence = Column(Boolean, default=False)  # 휴직 여부
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")
