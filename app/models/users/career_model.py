from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, DateTime
from app.core.database import Base
from datetime import datetime, UTC

from app.enums.user_management import ContractType


class Career(Base):
    __tablename__ = 'careers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    company = Column(String(255), nullable=False)  # 회사명
    contract_type = Column(Enum(ContractType), nullable=False)  # 계약유형
    start_date = Column(Date, nullable=False)  # 입사 연월
    end_date = Column(Date, nullable=True)  # 퇴사 연월
    job_title = Column(String(255), nullable=False)  # 직무
    department = Column(String(255), nullable=True)  # 조직
    position = Column(String(255), nullable=False)  # 직위

    created_at = Column(DateTime, default=datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC), nullable=False)
    deleted_yn = Column(String(1), default="N")