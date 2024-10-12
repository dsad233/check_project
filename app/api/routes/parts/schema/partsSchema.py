from pydantic import BaseModel


class PartCreate(BaseModel):
    name: str
    branch_id: int


class PartResponse(BaseModel):
    id: int
    name: str
