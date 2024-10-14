from fastapi import APIRouter, HTTPException

from app.api.routes.salary_bracket.schema.salary_bracket_schema import SalaryBracketResponse, SalaryBracketCreate, TaxBracketResponse
from app.models.policies.branchpolicies import SalaryBracket, TaxBracket
from app.core.database import async_session
from sqlalchemy import select

router = APIRouter()
db = async_session()

@router.get("/salary_bracket/{year}", response_model=SalaryBracketResponse)
async def get_salary_bracket(year: int):
    try:
        query = select(SalaryBracket).where(SalaryBracket.year == year, SalaryBracket.deleted_yn == 'N')
        result = await db.execute(query)
        salary_bracket = result.scalar_one_or_none()
        
        if salary_bracket is None:
                raise HTTPException(status_code=404, detail="Salary bracket not found")
            
        tax_brackets_query = select(TaxBracket).where(TaxBracket.salary_bracket_id == salary_bracket.id)
        tax_brackets_result = await db.execute(tax_brackets_query)
        tax_brackets_all = tax_brackets_result.scalars().all()
        
        tax_brackets_response = [TaxBracketResponse(
            id=tax_bracket.id,
            salary_bracket_id=tax_bracket.salary_bracket_id,
            lower_limit=tax_bracket.lower_limit,
            upper_limit=tax_bracket.upper_limit,
            tax_rate=tax_bracket.tax_rate,
            deduction=tax_bracket.deduction,
        ) for tax_bracket in tax_brackets_all]
        
        return SalaryBracketResponse(
            id=salary_bracket.id,
            year=salary_bracket.year,
            minimum_hourly_rate=salary_bracket.minimum_hourly_rate,
            minimum_monthly_rate=salary_bracket.minimum_monthly_rate,
            national_pension=salary_bracket.national_pension,
            health_insurance=salary_bracket.health_insurance,
            employment_insurance=salary_bracket.employment_insurance,
            long_term_care_insurance=salary_bracket.long_term_care_insurance,
            tax_brackets=tax_brackets_response,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/salary_bracket/{year}", response_model=SalaryBracketResponse)
async def create_salary_bracket(year: int, salary_bracket: SalaryBracketCreate):
    try:
        query = select(SalaryBracket).where(SalaryBracket.year == year, SalaryBracket.deleted_yn == 'N')
        result = await db.execute(query)
        salary_bracket = result.scalar_one_or_none()
        
        if salary_bracket is not None:
            raise HTTPException(status_code=400, detail="Salary bracket already exists")

        create = SalaryBracket(
            year=year,
            minimum_hourly_rate=salary_bracket.minimum_hourly_rate,
            minimum_monthly_rate=salary_bracket.minimum_monthly_rate,
            national_pension=salary_bracket.national_pension,
            health_insurance=salary_bracket.health_insurance,
            employment_insurance=salary_bracket.employment_insurance,
            long_term_care_insurance=salary_bracket.long_term_care_insurance,
        )
        db.add(create)
        await db.commit()
        
        tax_bracket_create = salary_bracket.tax_brackets
        
        for tax_bracket in tax_bracket_create:
            create_tax_bracket = TaxBracket(
                salary_bracket_id=create.id,
                lower_limit=tax_bracket.lower_limit,
                upper_limit=tax_bracket.upper_limit,
                tax_rate=tax_bracket.tax_rate,
                deduction=tax_bracket.deduction,
            )
            
            db.add(create_tax_bracket)
            await db.commit()
            
        return {"message": "Salary bracket created successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# @router.put("/salary_bracket/{year}", response_model=SalaryBracketResponse)
# async def update_salary_bracket(year: int, salary_bracket: SalaryBracketUpdate):
#     return await SalaryBracket.update_salary_bracket(year, salary_bracket)