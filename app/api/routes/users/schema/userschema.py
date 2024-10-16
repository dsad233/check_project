from datetime import date
from typing import Optional

from pydantic import BaseModel

# 유저 정보 추가를 위한 Pydantic 모델
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    phone_number: Optional[str] = None
    address: Optional[str] = None
    education: Optional[str] = None
    birth_date: Optional[date] = None
    hire_date: Optional[date] = None
    resignation_date: Optional[date] = None
    gender: Optional[str] = None
    part_id: Optional[int] = None
    branch_id: Optional[int] = None
    last_company: Optional[str] = None
    last_position: Optional[str] = None
    last_career_start_date: Optional[date] = None
    last_career_end_date: Optional[date] = None

# 유저 정보 업데이트를 위한 Pydantic 모델
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    education: Optional[str] = None
    birth_date: Optional[date] = None
    hire_date: Optional[date] = None
    resignation_date: Optional[date] = None
    gender: Optional[str] = None
    part_id: Optional[int] = None
    branch_id: Optional[int] = None
    last_company: Optional[str] = None
    last_position: Optional[str] = None
    last_career_start_date: Optional[date] = None
    last_career_end_date: Optional[date] = None

    class Config:
        arbitrary_types_allowed = True

# 직원의 Role 변경을 위한 Pydantic 모델
class RoleUpdate(BaseModel):
    role: str