from datetime import datetime

from pydantic import BaseModel


class AnnualLeaveCreate(BaseModel):
    type: str
    date_count: int
    application_date: datetime
    proposer_note: str
    manager_id: int


class AnnualLeaveApprove(BaseModel):
    status: str
    manager_note: str


class AnnualLeaveUpdate(BaseModel):
    type: str
    date_count: int
    application_date: datetime
    proposer_note: str


class AnnualLeaveListsResponse(BaseModel):
    id: int
    proposer_name: str
    work_part: str
    application_date: datetime
    type: str
    date_count: int
    status: str
    proposer_note: str
    manager_note: str
    updated_at: datetime
    manager_name: str
