from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users.career_model import Career
from app.schemas.user_management.career_schemas import CareerDto


async def add_career(
    session: AsyncSession,
    user_id: int,
    career_data: CareerDto
) -> Career:
    career = Career(
        user_id=user_id,
        company=career_data.company,
        contract_type=career_data.contract_type.value,
        job_title=career_data.job_title,
        position=career_data.position,
        department=career_data.department,
        start_date=career_data.start_date,
        end_date=career_data.end_date
    )
    session.add(career)
    return career

async def add_bulk_career(
    session: AsyncSession,
    user_id: int,
    career_list: list[CareerDto]
) -> list[Career]:
    career_records = [
        Career(
            user_id=user_id,
            company=career.company,
            contract_type=career.contract_type.value, 
            start_date=career.start_date,
            end_date=career.end_date,
            job_title=career.job_title,
            department=career.department,
            position=career.position
        ) for career in career_list
    ]
    session.add_all(career_records)
    return career_records