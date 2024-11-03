from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    Numeric
)

from app.core.database import Base
from datetime import date
from typing import Optional
from sqlalchemy import text
from pydantic import BaseModel

from app.enums.users import Role, Gender, MenuPermissions, EmploymentStatus

# Users와 Parts의 다대다 관계를 위한 연결 테이블
user_parts = Table('user_parts', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('part_id', Integer, ForeignKey('parts.id'))
)

user_menus = Table('user_menus', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('part_id', Integer, ForeignKey('parts.id'), nullable=False),
    Column('menu_name', Enum(
                       MenuPermissions,
                       values_callable=lambda obj: [e.value for e in obj]
                   ), nullable=False),
    Column('is_permitted', Boolean, default=False),
)

class Users(Base):
    __tablename__ = "users"

    # 유저 정보
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)  # 이름
    en_name = Column(String(255), nullable=True)  # 영문 이름
    email = Column(String(255), nullable=False, unique=True)  # 이메일
    password = Column(String(255), nullable=False)  # 비밀번호
    is_foreigner = Column(Boolean, nullable=False, default=False)  # 외국인 여부
    stay_start_date = Column(Date, nullable=True)  # 체류 시작일
    phone_number = Column(String(20), nullable=True)  # 전화번호
    address = Column(String(500), nullable=True)  # 주소
    education = Column(String(255), nullable=True)  # 학력
    birth_date = Column(Date, nullable=True)  # 생년월일
    gender = Column(Enum(*[e.value for e in Gender], name="user_gender"), nullable=False)  # 성별
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)  # 부서 ID
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)  # 지점 ID

    # 일자 관련 정보
    hire_date = Column(Date, nullable=True)  # 입사일
    sabbatical_start_date = Column(Date, nullable=True)  # 휴직 시작일
    sabbatical_end_date = Column(Date, nullable=True)  # 휴직 종료일
    resignation_date = Column(Date, nullable=True)  # 퇴사일

    # 연차 관련 정보
    total_leave_days = Column(Numeric(10, 2), nullable=True) # 총 연차 일수
    remaining_annual_leave = Column(Integer, nullable=True, default=0, server_default=text("0"))  # 잔여 연차

    # 이전 회사 정보
    last_company = Column(String(255), nullable=True)  # 이전 회사
    last_position = Column(String(255), nullable=True)  # 이전 회사 직위
    last_career_start_date = Column(Date, nullable=True)  # 이전 경력 시작일
    last_career_end_date = Column(Date, nullable=True)  # 이전 경력 종료일

    # 상태 관련 정보
    role = Column(
        Enum(
            *[e.value for e in Role],
            name="user_role"
        ),
        nullable=False,
        default=Role.EMPLOYEE
    )  # 권한
    position = Column(
        Enum(
            *[e.value for e in Role],
            name="user_position"
        ),
        nullable=False,
        default=Role.TEMPORARY
    )  # 직위
    employment_status = Column(
        Enum(
            *[e.value for e in EmploymentStatus],
            name="employment_status"
        ),
        nullable=False,
        default=EmploymentStatus.PERMANENT
    )  # 근무 상태

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")   # Y인 경우 삭제 회원으로 분류


class PersonnelRecordHistory(Base):
    __tablename__ = "personnel_record_histories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    personnel_record_category_id = Column(Integer, ForeignKey("personnel_record_categories.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    worker_comment = Column(String(255), nullable=False)
    admin_comment = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")


# 유저 정보 추가를 위한 Pydantic 모델
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    phone_number: str
    gender: str = None
    address: Optional[str] = None
    education: Optional[str] = None
    birth_date: Optional[date] = None
    hire_date: Optional[date] = None
    resignation_date: Optional[date] = None
    part_id: Optional[int] = None
    branch_id: Optional[int] = None
    last_company: Optional[str] = None
    last_position: Optional[str] = None
    last_career_start_date: Optional[date] = None
    last_career_end_date: Optional[date] = None


class AdminUserDto(BaseModel):
    id: int
    name: str
    phone_number: str
    part_id: int
    email: str
    role: str
    part_list: list[int] = []

    @classmethod
    async def build(cls, user: Users):
        return cls(
            id=user.id,
            name=user.name,
            phone_number=user.phone_number,
            part_id=user.part_id,
            email=user.email,
            role=user.role
        )

class AdminUsersDto(BaseModel):
    admin_users: list[AdminUserDto]

    @classmethod
    async def build(cls, users: list[Users]):
        return cls(
            admin_users=[await AdminUserDto.build(user=user) for user in users]
        )


class CreatedUserDto(BaseModel):
    id: int
    name: str
    email: str
    phone_number: Optional[str] = None
    address: Optional[str] = None
    education: Optional[str] = None
    birth_date: Optional[date] = None
    hire_date: Optional[date] = None
    resignation_date: Optional[date] = None

    class Config:
        from_attributes = True  # ORM 모드 사용

    @classmethod
    async def build(cls, user: Users):
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            phone_number=user.phone_number,
            address=user.address,
            education=user.education,
            birth_date=user.birth_date,
            hire_date=user.hire_date,
            resignation_date=user.resignation_date
        )

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