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
)

from app.core.database import Base
from app.enums.parts import PartAutoAnnualLeaveGrant


class Parts(Base):
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    name = Column(String(255), nullable=False)
    task = Column(String(500), nullable=True)
    color = Column(String(255), nullable=True)
    is_doctor = Column(Boolean, default=False)
    required_certification = Column(Boolean, default=False)
    leave_granting_authority = Column(Boolean, default=False)

    auto_annual_leave_grant = Column(
        Enum(*[e.value for e in PartAutoAnnualLeaveGrant], name="part_auto_annual_leave_grant"),
        nullable=False,
        default=PartAutoAnnualLeaveGrant.MANUAL_GRANT
    )
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(
        String(1), default="N"
    )  # annual_leaves = relationship("AnnualLeave", back_populates="part")
