from pydantic import BaseModel

class PartWorkPolicyCreate(BaseModel):
    work_policy_id: int
    work_start_time: str
    work_end_time: str
    lunch_start_time: str
    lunch_end_time: str
    break_time_1: str
    break_time_2: str


class PartWorkPolicyResponse(BaseModel):
    id: int
    work_start_time: str
    work_end_time: str
    lunch_start_time: str
    lunch_end_time: str
    break_time_1: str
    break_time_2: str