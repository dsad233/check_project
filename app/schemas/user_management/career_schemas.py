from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from app.enums.user_management import ContractType
from app.models.users.career_model import Career


class CareerDto(BaseModel):
    company: Optional[str] = Field(None, description="회사명")
    contract_type: Optional[ContractType] = Field(
        None,
        description="계약유형 (정규직/계약직/임시직/인턴)"
    )
    start_date: Optional[date] = Field(None, description="입사 연월")
    end_date: Optional[date] = Field(None, description="퇴사 연월")
    job_title: Optional[str] = Field(None, description="직무")
    department: Optional[str] = Field(None, description="조직")
    position: Optional[str] = Field(None, description="직위")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "company": "테스트 회사",
                "contract_type": "정규직",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "job_title": "백엔드 개발자",
                "department": "개발팀",
                "position": "사원"
            }
        }

    @classmethod
    async def build(cls, career: Career):
        return cls(
            id=career.id,
            company=career.company,
            contract_type=career.contract_type,
            start_date=career.start_date,
            end_date=career.end_date,
            job_title=career.job_title,
            department=career.department,
            position=career.position
        )