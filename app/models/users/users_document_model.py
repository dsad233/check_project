from datetime import datetime, UTC
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from app.core.database import Base

from sqlalchemy.orm import relationship


class Document(Base):
    __tablename__ = "document"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_name = Column(String(255), nullable=False)

    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

