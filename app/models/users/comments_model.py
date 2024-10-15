from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from app.core.database import Base
from app.common.dto.pagination_dto import PaginationDto
from app.common.dto.search_dto import BaseSearchDto

class Comments(Base):
    
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    
    content = Column(String(255), nullable=False)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

class CommentsCreate(BaseModel):
    content: str

class CommentsUpdate(BaseModel):
    content: str

class CommentsResponse(BaseModel):
    id: int
    author_name: str
    content: str
    created_at: datetime

class CommentListResponse(BaseModel):
    list: list[CommentsResponse]
    pagination: PaginationDto