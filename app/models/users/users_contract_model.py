from datetime import datetime, UTC
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Date, String, Enum
from app.core.database import Base
from app.enums.user_management import Status as SendMailStatus


class Contract(Base):
    __tablename__ = "contract"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    contract_name = Column(String(255), nullable=False)
    contract_type_id = Column(Integer, ForeignKey("document_policies.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    start_at = Column(Date, nullable=False)
    expired_at = Column(Date, nullable=True)


class ContractSendMailHistory(Base):
    __tablename__ = "contract_send_mail_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_id = Column(Integer, ForeignKey("contract.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    request_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(
        "contract_send_mail_history_status",
        Enum(SendMailStatus, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=SendMailStatus.SUCCESS
    )

    contract_start_at = Column(Date, nullable=False)
    contract_expired_at = Column(Date, nullable=True)

    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
