from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, Date, DateTime, Text, String

from app.core.database import Base


class WorkContractHistory(Base):
    __tablename__ = 'work_contract_history'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    work_contract_id = Column(Integer, ForeignKey('work_contract.id'))
    # salary_contract_id # 추후 급여 로직 구현 시 추가

    # 변경 사유, 비고
    change_reason = Column(Text, nullable=True)
    note = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default='N')
