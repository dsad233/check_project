from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users.education_model import Education
from app.schemas.user_management.education_schemas import EducationDto


async def add_education(
    session: AsyncSession,
    user_id: int,
    education_data: EducationDto
) -> Education:
    education = Education(
        user_id=user_id,
        school_name=education_data.school_name,
        major=education_data.major,
        degree=education_data.degree,
        admission_date=education_data.admission_date,
        graduation_date=education_data.graduation_date
    )
    session.add(education)
    return education

async def add_bulk_education(
    session: AsyncSession,
    user_id: int,
    education_list: list[EducationDto]
) -> list[Education]:
    education_records = [
        Education(
            user_id=user_id,
            school_type=edu.school_type,
            school_name=edu.school_name,
            graduation_type=edu.graduation_type,
            major=edu.major,
            admission_date=edu.admission_date,
            graduation_date=edu.graduation_date
        ) for edu in education_list
    ]
    session.add_all(education_records)
    return education_records