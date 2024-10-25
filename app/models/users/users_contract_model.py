from datetime import datetime, UTC
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Date, String
from app.core.database import Base


class Contract(Base):
    __tablename__ = "contract"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    contract_name = Column(String(255), nullable=False)
    contract_type_id = Column(Integer, ForeignKey("document_policies.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    expired_at = Column(Date, nullable=True)