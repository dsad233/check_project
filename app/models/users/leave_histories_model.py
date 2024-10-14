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


class LeaveHistories(Base):
    __tablename__ = "leave_histories"
    __table_args__ = (
        Index('idx_leave_history_user_id', 'user_id'),
        Index('idx_leave_history_date', 'date'),
        UniqueConstraint('user_id', 'date', name='uq_user_date'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    leave_category_id = Column(Integer, ForeignKey("leave_categories.id"), nullable=False)
    date = Column(Date, nullable=False)
    is_paid = Column(Boolean, nullable=False)
    description = Column(String(255), nullable=True)
    is_approved = Column(Boolean, default=False)  # 승인 여부
    is_leave_of_absence = Column(Boolean, default=False)  # 휴직 여부

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")