from pydantic import BaseModel

class UserLeaveResponse(BaseModel):
    id: int
    name: str
    part_name: str
    grant_type: str
    remaining_annual_leave: int