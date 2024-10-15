from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base

class Posts(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    content = Column(String(255), nullable=False)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")