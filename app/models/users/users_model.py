from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from datetime import date
from typing import Optional

from pydantic import BaseModel

from app.enums.users import Role, Gender, MenuPermissions

# Users와 Parts의 다대다 관계를 위한 연결 테이블
user_parts = Table('user_parts', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('part_id', Integer, ForeignKey('parts.id'))
)

user_menus = Table('user_menus', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('part_id', Integer, ForeignKey('parts.id'), nullable=False),
    Column('menu_name', Enum(MenuPermissions), nullable=False),
    Column('is_permitted', Boolean, default=False),
)

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)
    address = Column(String(500), nullable=True)
    education = Column(String(255), nullable=True)
    birth_date = Column(Date, nullable=True)
    hire_date = Column(Date, nullable=True)
    resignation_date = Column(Date, nullable=True)
    gender = Column(Enum(Gender, name="user_gender"), nullable=False)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)

    last_company = Column(String(255), nullable=True)
    last_position = Column(String(255), nullable=True)
    last_career_start_date = Column(Date, nullable=True)
    last_career_end_date = Column(Date, nullable=True)
    role = Column(Enum(Role, name="user_role"), nullable=False, default=Role.EMPLOYEE)


    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")


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