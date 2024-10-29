from pydantic import BaseModel
from typing import Optional


class UserLeaveResponse(BaseModel):
    id: Optional[int]
    name: Optional[str]
    part_name: Optional[str]
    grant_type: Optional[str]
    remaining_annual_leave: Optional[int]

