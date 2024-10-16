from datetime import datetime

from sqlalchemy import (Column, Integer, Float, ForeignKey, DateTime, String,)

from sqlalchemy.orm import relationship
from app.core.database import Base
from pydantic import Field
from pydantic_settings import BaseSettings

class UserSalary(Base):
    __tablename__ = "user_salaries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    
    monthly_salary = Column(Float, nullable=False)  # 월급
    annual_salary = Column(Float, nullable=False)  # 연봉
    hourly_wage = Column(Float, nullable=False)  # 시급

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    # 관계 설정
    user = relationship("Users", back_populates="salary")
    branch = relationship("Branches", back_populates="salaries")