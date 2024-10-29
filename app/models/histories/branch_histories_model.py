from sqlalchemy import Column, Integer, DateTime, String, JSON, ForeignKey, Enum
from app.core.database import Base
from datetime import datetime
from app.enums.branches import BranchHistoryType

class BranchHistories(Base):
    __tablename__ = "branch_histories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    snapshot_id = Column(String(255), nullable=False)
    history_type = Column(Enum(BranchHistoryType), nullable=False, index=True)
    history = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
