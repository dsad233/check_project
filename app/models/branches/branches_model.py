from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator
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
from sqlalchemy.orm import relationship

from app.common.dto.pagination_dto import PaginationDto
from app.core.database import Base


class Branches(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    representative_name = Column(String(255), nullable=False)
    registration_number = Column(String(255), nullable=False)
    call_number = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    corporate_seal = Column(String(255), nullable=True)
    nameplate = Column(String(255), nullable=True)
    mail_address = Column(String(255), nullable=False)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    user_leaves = relationship("UserLeavesDays", back_populates="branch", foreign_keys="[UserLeavesDays.branch_id]")

