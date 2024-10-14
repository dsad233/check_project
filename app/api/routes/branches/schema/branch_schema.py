from pydantic import BaseModel
from datetime import datetime
from app.common.dto.pagination_dto import PaginationDto

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(String(255), nullable=False)
#     created_at = Column(DateTime, default=datetime.now)
#     updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
#     deleted_yn = Column(String(1), default="N")

class BranchCreate(BaseModel):
    name: str

class BranchResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime
    deleted_yn: str

    class Config:
        from_attributes = True

class BranchListResponse(BaseModel):
    list: list[BranchResponse]
    pagination: PaginationDto

class BranchDelete(BaseModel):
    id: int