from pydantic import BaseModel
from typing import Optional


class PartIdWithName(BaseModel):
    id: Optional[int]
    name: Optional[str]

    class Config:
        from_attributes = True