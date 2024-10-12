from pydantic import BaseModel

class PartCreate(BaseModel):
    name: str
    description: str
    branch_id: int
