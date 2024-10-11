from pydantic import BaseModel
from datetime import datetime

class application_Status_Enum:
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class OverTimeCrete(BaseModel):
    application_note : str
    proposer_note : str
    

class OverTimeEdit(BaseModel):
    manager_id : int
    proposer_note : str                                                                
    processed_date : datetime.now
    application_status : application_Status_Enum