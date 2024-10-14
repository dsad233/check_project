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

class AllowancePolicies(Base):
    __tablename__ = "allowance_policies"
    # __table_args__ = (
    #     Index('idx_part_policies_part_id', 'part_id')
    # )
    id = Column(Integer, primary_key=True, autoincrement=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    
    comprehensive_overtime = Column(Boolean, default=False) # 포괄산정 연장근무수당
    annual_leave = Column(Boolean, default=False) # 연차수당
    holiday_work = Column(Boolean, default=False) # 휴일수당
    job_duty = Column(Boolean, default=False) # 직무수당
    meal = Column(Boolean, default=False) # 식대

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")