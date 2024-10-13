from typing import Optional

from pydantic import BaseModel, Field


class PartCreate(BaseModel):
    name: str = Field(..., min_length=1, description="파트 이름")
    task: str = Field(..., min_length=1, description="파트 업무")
    is_doctor: bool
    required_certification: Optional[str] = None
    leave_granting_authority: Optional[str] = None


class PartUpdate(BaseModel):
    name: Optional[str] = None
    task: Optional[str] = None
    is_doctor: Optional[bool] = None
    required_certification: Optional[str] = None
    leave_granting_authority: Optional[str] = None


class PartResponse(BaseModel):
    id: int
    name: str
    task: Optional[str] = None
    is_doctor: bool
    required_certification: Optional[str] = None
    leave_granting_authority: Optional[str] = None
