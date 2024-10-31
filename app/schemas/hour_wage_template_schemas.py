from datetime import time
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.common.dto.pagination_dto import PaginationDto



class HourWageTemplateRequest(BaseModel):
    part_id: Optional[int] = Field(description="직책 ID")
    name: str = Field(description="템플릿 명")
    start_time: time = Field(description="시작 시간")
    end_time: time = Field(description="종료 시간")
    hour_wage: int = Field(description="시급")
    home_hour_wage: int = Field(description="재택근무시급 시급")

    @field_validator('part_id', mode='before')
    @classmethod
    def set_part_id(cls, v):
        return None if v == 0 else v
    

class HourWageTemplateResponse(BaseModel):
    id: int = Field(description="아이디")
    part_id: Optional[int] = Field(default=0, description="직책 ID")
    name: str = Field(description="템플릿 명")
    start_time: time = Field(description="시작 시간")
    end_time: time = Field(description="종료 시간")
    hour_wage: int = Field(description="시급")
    home_hour_wage: int = Field(description="재택근무시급 시급")

    @field_validator('part_id', mode='before')
    @classmethod
    def set_part_id(cls, v):
        return 0 if v is None else v

    class Config:
        from_attributes = True


class HourWageTemplatesResponse(BaseModel):
    data: list[HourWageTemplateResponse]
    pagination: PaginationDto
