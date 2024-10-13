from datetime import date
from typing import Optional

from pydantic import BaseModel


class ClosedDayCreate(BaseModel):
    closed_day_date: date
    memo: Optional[str] = None

    class Config:
        from_attributes = True
