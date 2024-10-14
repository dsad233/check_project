from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from app.models.salary.salary_bracket_model import SalaryBracket, TaxBracket, SalaryBracketResponse, TaxBracketResponse, SalaryBracketCreate
from app.core.database import async_session
from app.middleware.tokenVerify import validate_token
from app.models.users.users_model import Users

router = APIRouter()
db = async_session()

@router.get("/{year}", response_model=SalaryBracketResponse)
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
            
            minimum_pension_income=salary_bracket.minimum_pension_income,
            maximum_pension_income=salary_bracket.maximum_pension_income,
            maximum_national_pension=salary_bracket.maximum_national_pension,
            minimum_health_insurance=salary_bracket.minimum_health_insurance,
            maximum_health_insurance=salary_bracket.maximum_health_insurance,
            
            local_income_tax_rate=salary_bracket.local_income_tax_rate,
            
            tax_brackets=tax_brackets_response,
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{year}")
async def create_salary_bracket(year: int, salary_bracket_create: SalaryBracketCreate, current_user: Users = Depends(validate_token)):
    if current_user.role.strip() != "MSO 최고권한":
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    async with async_session() as session:
        async with session.begin():
            try:
                query = select(SalaryBracket).where(SalaryBracket.year == year, SalaryBracket.deleted_yn == 'N')
                result = await session.execute(query)
                existing_salary_bracket = result.scalar_one_or_none()
                
                if existing_salary_bracket is not None:
                    raise HTTPException(status_code=400, detail="Salary bracket already exists")

                new_salary_bracket = SalaryBracket(
                    year=year,
                    minimum_hourly_rate=salary_bracket_create.minimum_hourly_rate,
                    minimum_monthly_rate=salary_bracket_create.minimum_monthly_rate,
                    
                    national_pension=salary_bracket_create.national_pension,
                    health_insurance=salary_bracket_create.health_insurance,
                    employment_insurance=salary_bracket_create.employment_insurance,
                    long_term_care_insurance=salary_bracket_create.long_term_care_insurance,
                    
                    minimum_pension_income=salary_bracket_create.minimum_pension_income,
                    maximum_pension_income=salary_bracket_create.maximum_pension_income,
                    maximum_national_pension=salary_bracket_create.maximum_national_pension,
                    minimum_health_insurance=salary_bracket_create.minimum_health_insurance,
                    maximum_health_insurance=salary_bracket_create.maximum_health_insurance,
                    
                    local_income_tax_rate=salary_bracket_create.local_income_tax_rate,
                )
                session.add(new_salary_bracket)
                await session.flush()
                
                for tax_bracket in salary_bracket_create.tax_brackets:
                    new_tax_bracket = TaxBracket(
                        salary_bracket_id=new_salary_bracket.id,
                        lower_limit=tax_bracket.lower_limit,
                        upper_limit=tax_bracket.upper_limit,
                        tax_rate=tax_bracket.tax_rate,
                        deduction=tax_bracket.deduction,
                    )
                    session.add(new_tax_bracket)
                
                await session.commit()
                
                return {"message": "Salary bracket created successfully"}
            except Exception as e:
                await session.rollback()
                print(e)
                raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{year}")
async def delete_salary_bracket(year: int, current_user: Users = Depends(validate_token)):
    if current_user.role.strip() != "MSO 최고권한":
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    async with async_session() as session:
        async with session.begin():
            try:
                query = select(SalaryBracket).where(SalaryBracket.year == year, SalaryBracket.deleted_yn == 'N')
                result = await session.execute(query)
                salary_bracket = result.scalar_one_or_none()
                
                if salary_bracket is None:
                    raise HTTPException(status_code=404, detail="Salary bracket not found")
                
                salary_bracket.deleted_yn = 'Y'
                await session.commit()
                
                return {"message": "Salary bracket deleted successfully"}
            except Exception as e:
                await session.rollback()
                print(e)
                raise HTTPException(status_code=500, detail=str(e))
