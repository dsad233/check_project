from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, Date, DateTime

from app.core.database import Base


class UserWorkContractHistoryModel(Base):
    __tablename__ = 'user_work_contract_history'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    work_contract_id = Column(Integer, ForeignKey('work_contract.id'))

    start_date = Column(Date)
    end_date = Column(Date)

    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    # 추후 __init__ 파일에 추가
    # user = relationship("UserModel", back_populates="work_contract_history")
    # contract = relationship("WorkContractModel", back_populates="user_work_contract_history")
