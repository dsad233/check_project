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


class AnnualLeave(Base):
    __tablename__ = "annual_leave"
    __table_args__ = (
        Index('idx_annual_leave_user_id', 'user_id'),
        Index('idx_annual_leave_date', 'date'),
        UniqueConstraint('user_id', 'date', name='uq_user_date'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    leave_type = Column(Enum('유급휴가', '유급 오전반차', '유급 오후반차', '무급휴가', '무급 오전반차', '무급 오후반차', name='leave_type'), nullable=False)
    is_paid = Column(Boolean, nullable=False)
    description = Column(String(255), nullable=True)
    is_approved = Column(Boolean, default=False)  # 승인 여부
    is_leave_of_absence = Column(Boolean, default=False)  # 휴직 여부
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    user = relationship("Users", back_populates="annual_leaves")