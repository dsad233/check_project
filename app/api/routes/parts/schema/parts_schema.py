from typing import Optional

from pydantic import BaseModel


class PartCreate(BaseModel):
    name: str
    branch_id: int
    task: str
    is_doctor: bool
    required_certification: Optional[str] = None
    leave_granting_authority: Optional[str] = None


class PartResponse(BaseModel):
    id: int
    name: str
    task: Optional[str] = None
    is_doctor: bool
    required_certification: Optional[str] = None
    leave_granting_authority: Optional[str] = None
