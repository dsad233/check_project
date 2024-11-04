from sqlalchemy.ext.asyncio import AsyncSession


async def add_career(
    session: AsyncSession,
    user_id: int,
    career_data: CareerDto
) -> Career:
    career = Career(
        user_id=user_id,
        company_name=career_data.company_name,
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
            contract_type=career.contract_type,
            start_date=career.start_date,
            end_date=career.end_date,
            job_title=career.job_title,
            department=career.department,
            position=career.position
        ) for career in career_list
    ]
    session.add_all(career_records)
    return career_records