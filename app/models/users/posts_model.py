from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from app.core.database import Base
from app.common.dto.pagination_dto import PaginationDto
from app.common.dto.search_dto import BaseSearchDto

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

class PostsCreate(BaseModel):
    title: str
    content: str

class PostsUpdate(BaseModel):
    title: str
    content: str

class PostsResponse(BaseModel):
    id: int
    title: str
    content: str
    author_name: str
    created_at: datetime

class PostListResponse(BaseModel):
    list: list[PostsResponse]
    pagination: PaginationDto

class PostsSearchDto(BaseSearchDto):
    title: Optional[str] = None
    content: Optional[str] = None
    author_name: Optional[str] = None