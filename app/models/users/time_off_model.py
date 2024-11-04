from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Enum as SQLAlchemyEnum

from app.enums.users import TimeOffType
from app.core.database import Base


class TimeOff(Base):
    __tablename__ = 'time_offs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    time_off_type = Column(
        SQLAlchemyEnum(TimeOffType),
        nullable=False
    )
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    description = Column(String(500))

    created_at = Column(DateTime, default=lambda: datetime.now(timezone('Asia/Seoul')), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone('Asia/Seoul')),
                       onupdate=lambda: datetime.now(timezone('Asia/Seoul')),
                       nullable=False)
    deleted_yn = Column(String(1), default="N")

    def __repr__(self):
        return f"<TimeOff(id={self.id}, user_id={self.user_id}, time_off_type={self.time_off_type})>"