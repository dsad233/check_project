from sqlalchemy import Column, Integer, DateTime, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import UTC, datetime

class Commutes(Base):
    __tablename__ = "commutes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    clock_in = Column(DateTime, nullable=False, default=datetime.now(UTC))
    clock_out = Column(DateTime)
    work_hours = Column(Float)
    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    deleted_yn = Column(String(1), default='N')
