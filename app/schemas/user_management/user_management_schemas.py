from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel, ConfigDict

from app.schemas.user_management.career_schemas import CareerDto
from app.schemas.user_management.time_off_schemas import TimeOffResponseDto


class PartDTO(BaseModel):
    id: int
    name: str

    branch_id: Optional[int] = None
    is_doctor: Optional[bool] = None
    leave_granting_authority: Optional[bool] = None
    required_certification: Optional[bool] = None
    task: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_yn: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class BranchDTO(BaseModel):
    address: str
    call_number: str
    code: str
    corporate_seal: Optional[str]
    created_at: datetime
    deleted_yn: str
    id: int
    mail_address: str
    name: str
    nameplate: Optional[str]
    registration_number: str
    representative_name: str
    updated_at: datetime

class BranchListDto(BaseModel):
    id: int
    code: str
    address: str
    mail_address: str
    name: str

class PartListDto(BaseModel):
    id: int
    branch_id: Optional[int] = None
    is_doctor: Optional[bool] = None
    name: str
    task: Optional[str] = None


    model_config = ConfigDict(from_attributes=True)


class EducationDTO(BaseModel):
    id: int
    school_type: Optional[str]
    school_name: Optional[str]
    graduation_type: Optional[str]
    major: Optional[str]
    admission_date: Optional[datetime]
    graduation_date: Optional[datetime]



class UserDTO(BaseModel):
    id: int
    name: str
    en_name: Optional[str] = None
    gender: Optional[str] = None
    email: str
    hire_date: Optional[date] = None
    resignation_date: Optional[date] = None
    parts: Optional[List[PartDTO]] = None
    branch: Optional[BranchDTO] = None
    role: str
    position: Optional[str] = None
    employment_status: Optional[str] = None
    last_activity: Optional[datetime] = None
    birth_date: Optional[datetime] = None
    resident_registration_number: Optional[str] = None
    phone_number: Optional[str] = None
    monthly_salary: Optional[float] = None
    annual_salary: Optional[float] = None
    is_foreigner: Optional[bool] = None
    stay_start_date: Optional[date] = None
    stay_end_date: Optional[date] = None
    address: Optional[str] = None
    detail_address: Optional[str] = None
    education: Optional[List[EducationDTO]] = None
    total_leave_days: Optional[float] = None
    remaining_annual_leave: Optional[int] = None
    time_off: Optional[List[TimeOffResponseDto]] = None
    career: Optional[List[CareerDto]] = None

    @classmethod
    def from_orm(cls, user, last_activity=None, monthly_salary=None, annual_salary=None):
        parts = None

        if user.part:
            parts = [PartDTO(
                id=user.part.id,
                branch_id=user.part.branch_id,
                name=user.part.name,
                task=user.part.task,
                is_doctor=user.part.is_doctor,
                required_certification=user.part.required_certification,
                leave_granting_authority=user.part.leave_granting_authority,
                created_at=user.part.created_at,
                updated_at=user.part.updated_at,
            )]

        educations = None
        if hasattr(user, 'educations') and user.educations:
            educations = [EducationDTO(**edu.__dict__) for edu in user.educations]

        careers = None
        if hasattr(user, 'careers') and user.careers:
            careers = [CareerDto(**career.__dict__) for career in user.careers]

        time_offs = None
        if hasattr(user, 'time_offs') and user.time_offs:
            latest_time_off = user.time_offs[0] if user.time_offs else None
            if latest_time_off:
                time_offs = [TimeOffResponseDto(**latest_time_off.__dict__)]

        return cls(
            id=user.id,
            name=user.name,
            en_name=user.en_name,
            email=user.email,
            is_foreigner=user.is_foreigner,
            stay_start_date=user.stay_start_date,
            stay_end_date=user.stay_end_date,
            phone_number=user.phone_number,
            address=user.address,
            detail_address=user.detail_address,
            birth_date=user.birth_date,
            resident_registration_number=user.resident_registration_number,
            gender=user.gender,
            hire_date=user.hire_date,
            resignation_date=user.resignation_date,
            parts=parts,
            branch=BranchDTO(**user.branch.__dict__) if user.branch else None,
            role=user.role,
            position=user.position,
            employment_status=user.employment_status,
            last_activity=last_activity,
            monthly_salary=monthly_salary,
            annual_salary=annual_salary,
            total_leave_days=user.total_leave_days,
            remaining_annual_leave=user.remaining_annual_leave,
            education=educations,
            career=careers,
            time_off=time_offs
        )

    @classmethod
    def from_user_data(cls, user, last_activity=None, monthly_salary=None, annual_salary=None):
        """사용자 상세 정보를 위한 별도 메서드"""
        return cls.from_orm(user, last_activity, monthly_salary, annual_salary)




class CurrentUserDTO(BaseModel):
    id: int
    name: str
    email: str
    role: str
    parts: Optional[List[PartDTO]]
    branch: Optional[BranchDTO]

    @classmethod
    def from_user(cls, user):
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            parts=[PartDTO(**user.part.__dict__)] if user.part else None,
            branch=BranchDTO(**user.branch.__dict__) if user.branch else None
        )

class UserListDto(BaseModel):
    id: int
    branch: Optional[BranchListDto] = None
    gender: Optional[str] = None
    name: str
    en_name: Optional[str] = None
    parts: Optional[List[PartListDto]] = None
    birth_date: Optional[date] = None
    phone_number: Optional[str] = None
    email: str
    hire_date: Optional[date] = None
    resignation_date: Optional[date] = None
    monthly_salary: Optional[float] = None
    annual_salary: Optional[float] = None
    role: str
    position: Optional[str] = None
    employment_status: Optional[str] = None

    @classmethod
    def from_orm(cls, user, last_activity=None, monthly_salary=None, annual_salary=None):
        parts = None

        if user.part:
            parts = [PartListDto(
                id=user.part.id,
                branch_id=user.part.branch_id,
                name=user.part.name,
                task=user.part.task,
                is_doctor=user.part.is_doctor,
            )]

        return cls(
            id=user.id,
            name=user.name,
            en_name=user.en_name,
            gender=user.gender,
            email=user.email,
            hire_date=user.hire_date,
            resignation_date=user.resignation_date,
            parts=parts,
            branch=BranchListDto(**user.branch.__dict__) if user.branch else None,
            role=user.role,
            birth_date=user.birth_date,
            phone_number=user.phone_number,
            employment_status=user.employment_status,
            position=user.position,
            monthly_salary=monthly_salary,
            annual_salary=annual_salary
        )



class UserListResponseDTO(BaseModel):
    message: str
    data: List[UserListDto]
    total: int
    count: int
    page: int
    record_size: int