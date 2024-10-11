from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class AnnualLeaveType(str, Enum):
    PAID_FULL_DAY = "paid annual leave"
    UNPAID_FULL_DAY = "unpaid annual leave"
    PAID_HALF_DAY = "paid half day leave"
    UNPAID_HALF_DAY = "unpaid half day leave"
    
class AnnualLeaveStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class AnnualLeaveCreate(BaseModel):
    type : AnnualLeaveType
    date_count : int
    application_date : datetime
    proposer_note : str
    
class AnnualLeaveApprove(BaseModel):
    status : AnnualLeaveStatus
    manager_note : str
    
class AnnualLeaveUpdate(BaseModel):
    type : AnnualLeaveType
    date_count : int
    application_date : datetime
    proposer_note : str
    
class AnnualLeaveListsResponse(BaseModel):
    id : int
    proposer_name : str
    work_part : str
    application_date : datetime
    type : AnnualLeaveType
    date_count : int
    status : AnnualLeaveStatus
    proposer_note : str
    manager_note : str
    updated_at : datetime
    manager_name : str
    