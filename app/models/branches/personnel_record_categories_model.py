from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from app.core.database import Base
from sqlalchemy.orm import relationship

class PersonnelRecordCategory(Base):
    __tablename__ = "personnel_record_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(500))

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    branch = relationship("Branches", back_populates="personnel_record_categories")


class PersonnelRecordCategoryDto(BaseModel):
    id: int | None = None
    name: str
    description: str | None = None

    class Config:
        from_attributes = True