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
    Numeric, select
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import Base
from datetime import date
from typing import Optional, Dict, List, Any
from sqlalchemy import text
from pydantic import BaseModel, ConfigDict

from app.enums.users import Role, Gender, MenuPermissions, EmploymentStatus
from app.schemas.user_management.career_schemas import CareerDto
from app.schemas.user_management.education_schemas import EducationDto

# Users와 Parts의 다대다 관계를 위한 연결 테이블
user_parts = Table('user_parts', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('part_id', Integer, ForeignKey('parts.id'))
)

user_menus = Table('user_menus', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('part_id', Integer, ForeignKey('parts.id'), nullable=True),
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
    stay_end_date = Column(Date, nullable=True)  # 체류 종료일

    phone_number = Column(String(20), nullable=True)  # 전화번호
    address = Column(String(500), nullable=True)  # 주소
    detail_address = Column(String(500), nullable=True)  # 상세 주소

    birth_date = Column(Date, nullable=True)  # 생년월일
    resident_registration_number = Column(String(20), nullable=True)  # 주민등록번호
    gender = Column(Enum(*[e.value for e in Gender], name="user_gender"), nullable=False)  # 성별
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=True)  # 부서 ID
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)  # 지점 ID

    # 일자 관련 정보
    hire_date = Column(Date, nullable=True)  # 입사일
    resignation_date = Column(Date, nullable=True)  # 퇴사일

    # 연차 관련 정보
    total_leave_days = Column(Numeric(10, 2), nullable=True)  # 총 연차 일수
    remaining_annual_leave = Column(Integer, nullable=True, default=0, server_default=text("0"))  # 잔여 연차

    # 상태 관련 정보
    role = Column(
        Enum(
            *[e.value for e in Role],
            name="user_role"
        ),
        nullable=False,
        default=Role.EMPLOYEE
    )  # 권한
    position = Column(String(20), nullable=False, default="직원")  # 직위
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
    deleted_yn = Column(String(1), default="N")  # Y인 경우 삭제 회원으로 분류


class PersonnelRecordHistory(Base):
    __tablename__ = "personnel_record_histories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    personnel_record_category_id = Column(Integer, ForeignKey("personnel_record_categories.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    worker_comment = Column(String(255), nullable=False)
    admin_comment = Column(String(255), nullable=False) # TODO: create_date 추가?
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")


# 유저 정보 추가를 위한 Pydantic 모델
class UserCreate(BaseModel):
    name: Optional[str] = None
    en_name: Optional[str] = None
    email: str
    password: str
    phone_number: Optional[str] = None
    address: Optional[str] = None
    detail_address: Optional[str] = None
    birth_date: Optional[date] = None
    resident_registration_number: Optional[str] = None

    # 외래 키
    branch_id: Optional[int] = None
    

    # 추가 정보
    role: Optional[str] = Role.TEMPORARY.value
    gender: Optional[str] = None
    is_foreigner: Optional[bool] = None
    stay_start_date: Optional[date] = None
    stay_end_date: Optional[date] = None

    # 관계 필드
    educations: Optional[list[EducationDto]] = None
    careers: Optional[list[CareerDto]] = None


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
    name: Optional[str] = None
    en_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    detail_address: Optional[str] = None
    birth_date: Optional[date] = None
    resident_registration_number: Optional[str] = None

    branch_id: Optional[int] = None
    role: Optional[str] = None
    gender: Optional[str] = None
    is_foreigner: Optional[bool] = None
    stay_start_date: Optional[date] = None
    stay_end_date: Optional[date] = None

    educations: Optional[list[EducationDto]] = None
    careers: Optional[list[CareerDto]] = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    async def build(cls, user: Users, session: AsyncSession):
        # relationship을 미리 로드
        stmt = select(Users).where(Users.id == user.id).options(
            selectinload(Users.educations),
            selectinload(Users.careers)
        )
        result = await session.execute(stmt)
        user = result.scalar_one()

        return cls(
            id=user.id,
            name=user.name,
            en_name=user.en_name,
            email=user.email,
            phone_number=user.phone_number,
            address=user.address,
            detail_address=user.detail_address,
            birth_date=user.birth_date,
            educations=[await EducationDto.build(edu) for edu in user.educations] if user.educations else None,
            careers=[await CareerDto.build(career) for career in user.careers] if user.careers else None
        )


# 유저 정보 업데이트를 위한 Pydantic 모델
class UserUpdate(BaseModel):
    branch_id: Optional[int] = None
    part_id: Optional[int] = None
    role: Optional[str] = None
    name: Optional[str] = None
    en_name: Optional[str] = None
    phone_number: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    detail_address: Optional[str] = None
    email: Optional[str] = None
    educations: Optional[List[Dict[str, Any]]] = None
    careers: Optional[List[Dict[str, Any]]] = None
    birth_date: Optional[date] = None
    is_foreigner: Optional[bool] = None
    stay_start_date: Optional[date] = None
    stay_end_date: Optional[date] = None
    hire_date: Optional[date] = None
    resignation_date: Optional[date] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


# 직원의 Role 변경을 위한 Pydantic 모델
class RoleUpdate(BaseModel):
    role: str