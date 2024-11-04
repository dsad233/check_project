from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from app.models.users.education_model import Education


class EducationDto(BaseModel):
    """교육 정보 DTO"""
    school_type: Optional[SchoolType] = Field(
        None,
        description="학교 유형 (초등학교, 중학교, 고등학교, 대학교, 대학원)"
    )
    school_name: Optional[str] = Field(
        None,
        description="학교명",
        example="서울대학교"
    )
    graduation_type: Optional[GraduationType] = Field(
        None,
        description="졸업 상태 (졸업, 재학중, 휴학, 중퇴)"
    )
    major: Optional[str] = Field(
        None,
        description="전공",
        example="컴퓨터공학"
    )
    admission_date: Optional[date] = Field(
        None,
        description="입학일",
        example="2020-03-01"
    )
    graduation_date: Optional[date] = Field(
        None,
        description="졸업일",
        example="2024-02-29"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "school_type": "대학교",
                "school_name": "한국대학교",
                "graduation_type": "졸업",
                "major": "컴퓨터공학",
                "admission_date": "2020-03-01",
                "graduation_date": "2024-02-29"
            }
        }

    @classmethod
    async def build(cls, education: Education):
        return cls(
            id=education.id,
            school_type=education.school_type,
            school_name=education.school_name,
            graduation_type=education.graduation_type,
            major=education.major,
            admission_date=education.admission_date,
            graduation_date=education.graduation_date
        )