from datetime import datetime

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
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.enums.branches import RestDayType


# 휴무일 테이블
class RestDays(Base):
    __tablename__ = "rest_days"
    __table_args__ = (
        Index("idx_rest_days_branch_id", "branch_id"),
        Index("idx_rest_days_date", "date"),
        UniqueConstraint("branch_id", "date", name="uq_branch_part_date"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    date = Column(Date, nullable=False)
    rest_type = Column(Enum(*[e.value for e in RestDayType], name="rest_day_type"), nullable=False)
    description = Column(String(255), nullable=True)
    is_paid = Column(Boolean, default=False)  # 유급 휴일 여부
    is_holiday_work_allowed = Column(Boolean, default=False)  # 휴일근무 허용 여부

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")
