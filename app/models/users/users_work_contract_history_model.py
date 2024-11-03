from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, Date, DateTime, Text, String

from app.core.database import Base


class ContractHistory(Base):
    __tablename__ = 'contract_history'

    id = Column(Integer, primary_key=True)
    contract_info_id = Column(Integer, ForeignKey('contract_info.id'))
    user_id = Column(Integer, ForeignKey('users.id'))

    # 변경 사유, 비고
    change_reason = Column(Text, nullable=True)
    note = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default='N')
