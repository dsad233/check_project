from sqlalchemy import Column, Integer, String, Date, DateTime, func, ForeignKey
from app.core.database import Base


class ClosedDays(Base):
    __tablename__ = "closed_days"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=False, index=True)
    closed_day_date = Column(Date, nullable=False, index=True)
    memo = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_yn = Column(String(1), default="N")