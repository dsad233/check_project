from pydantic import BaseModel
from datetime import datetime
from app.common.dto.pagination_dto import PaginationDto

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     code = Column(String(255), nullable=False)
#     name = Column(String(255), nullable=False)
#     representative_name = Column(String(255), nullable=False)
#     registration_number = Column(String(255), nullable=False)
#     call_number = Column(String(255), nullable=False)
#     address = Column(String(255), nullable=False)
#     corporate_seal = Column(String(255), nullable=False)
#     nameplate = Column(String(255), nullable=False)
#     mail_address = Column(String(255), nullable=False)
#     created_at = Column(DateTime, default=datetime.now)
#     updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
#     deleted_yn = Column(String(1), default="N")

class BranchCreate(BaseModel):
    name: str
    code: str

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