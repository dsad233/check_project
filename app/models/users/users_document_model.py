from datetime import datetime, UTC
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Enum, Date
from app.core.database import Base
from app.enums.user_management import DocumentSendStatus


class Document(Base):
    __tablename__ = "document"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_name = Column(String(255), nullable=False)

    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))


class DocumentSendHistory(Base):
    __tablename__ = "document_send_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("document.id"), nullable=False)
    request_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    request_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    request_date = Column(Date, nullable=False)
    request_reason = Column(String(255), nullable=False)
    status = Column(
        "document_send_history_status",
        Enum(DocumentSendStatus, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=DocumentSendStatus.PENDING
    )

    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    deleted_yn = Column(String(1), default="N")
