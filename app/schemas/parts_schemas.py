from pydantic import BaseModel, Field
from typing import Optional


class PartIdWithName(BaseModel):
    id: Optional[int]
    name: Optional[str]

    class Config:
        from_attributes = True


class PartRequest(BaseModel):
    name: Optional[str] = Field(default=None, description="파트 이름")
    task: Optional[str] = Field(default=None, description="파트 업무")
    color: Optional[str] = Field(default=None, description="파트 색상")
    is_doctor: Optional[bool] = Field(default=False, description="의사 여부")
    required_certification: Optional[bool] = Field(default=False, description="인증 여부")


class PartResponse(BaseModel):
    id: int
    name: str
    task: Optional[str] = None
    color: Optional[str] = None
    is_doctor: bool
    required_certification: bool
    leave_granting_authority: bool
    
    class Config:
        from_attributes = True