from datetime import datetime, UTC
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Date, String, Enum, Boolean
from app.core.database import Base
from app.enums.user_management import Status as SendMailStatus, ContractStatus


class Contract(Base):
    __tablename__ = "contract"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    work_contract_id = Column(Integer, ForeignKey("work_contract.id"), nullable=False)

    # 계약서 정보
    contract_name = Column(String(255), nullable=False)
    contract_type_id = Column(Integer, ForeignKey("document_policies.id"), nullable=False)
    modusign_id = Column(String(255), nullable=True, unique=True)  # 모두싸인 ID
    contract_url = Column(String(255), nullable=False, unique=True) # 계약서 URL / 모두싸인 URL or 계약서 URL중 하나는 존재
    contract_status = Column(
        "contract_status",
        Enum(
            ContractStatus,
            values_callable=lambda obj: [e.value for e in obj]
        ),
        nullable=False,
        default=ContractStatus.PENDING
    )  # 계약 상태
    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    deleted_yn = Column(String(1), default="N")


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
