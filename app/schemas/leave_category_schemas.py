from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.schemas.parts_schemas import PartIdWithName


class LeaveCategoryDto(BaseModel):
    id: Optional[int] = Field(default=None, description="휴무 ID")
    name: str = Field(description="휴무 명")
    leave_count: int = Field(description="차감 일수")
    is_paid: bool = Field(description="유급 여부")

    @field_validator("id")
    def validate_file_extension(cls, v):
        if v == "" or v == 0:
            return None
        return v

    model_config = ConfigDict(from_attributes=True)


class LeaveExcludedPartResponse(BaseModel):
    id: int = Field(..., gt=0)
    leave_category_id: int = Field(..., gt=0)
    part_id: int = Field(..., gt=0)

    model_config = ConfigDict(from_attributes=True)


class LeaveCategoryWithExcludedPartsDto(BaseModel):
    leave_category: LeaveCategoryDto
    excluded_parts: list[PartIdWithName] = []