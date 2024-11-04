from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    ForeignKey,
)
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


class PersonnelRecordCategory(Base):
    __tablename__ = "personnel_record_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

