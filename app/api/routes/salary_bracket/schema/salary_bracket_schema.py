from pydantic import BaseModel

class SalaryBracketResponse(BaseModel):
    id: int
    year: int
    minimum_hourly_rate: int
    minimum_monthly_rate: int
    national_pension: int
    health_insurance: int
    employment_insurance: int
    long_term_care_insurance: int
    minimun_pension_income: int
    maximum_pension_income: int
    maximum_national_pension: int
    minimun_health_insurance: int
    maximum_health_insurance: int
    income_tax: int
    local_income_tax: int
    tax_brackets: list["TaxBracketResponse"]
    
class SalaryBracketCreate(BaseModel):
    year: int
    minimum_hourly_rate: int
    minimum_monthly_rate: int
    national_pension: int
    health_insurance: int
    employment_insurance: int
    long_term_care_insurance: int
    minimun_pension_income: int
    maximum_pension_income: int 
    maximum_national_pension: int
    minimun_health_insurance: int
    maximum_health_insurance: int
    income_tax: int
    local_income_tax: int
    tax_brackets: list["TaxBracketCreate"]

class TaxBracketResponse(BaseModel):
    id: int
    salary_bracket_id: int
    lower_limit: int
    upper_limit: int
    tax_rate: float
    deduction: int
    
class TaxBracketCreate(BaseModel):
    lower_limit: int
    upper_limit: int
    tax_rate: float
    deduction: int