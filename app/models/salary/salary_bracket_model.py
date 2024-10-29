from datetime import datetime

from pydantic import BaseModel, field_validator
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


# 급여 테이블 #
class SalaryBracket(Base):
    __tablename__ = "salary_brackets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False)  # 연도
    minimum_hourly_rate = Column(Float, nullable=False)  # 최저 시급
    minimum_monthly_rate = Column(Float, nullable=False)  # 최저 월급

    national_pension = Column(Float, nullable=False)  # 국민연금
    health_insurance = Column(Float, nullable=False)  # 건강보험
    employment_insurance = Column(Float, nullable=False)  # 고용보험
    long_term_care_insurance = Column(Float, nullable=False)  # 장기요양보험

    minimum_pension_income = Column(Float, nullable=False)  # 연금소득 최저
    maximum_pension_income = Column(Float, nullable=False)  # 연금소득 최대
    maximum_national_pension = Column(Float, nullable=False)  # 국민연금 최대
    minimum_health_insurance = Column(Float, nullable=False)  # 건강보험 최저
    maximum_health_insurance = Column(Float, nullable=False)  # 건강보험 최대

    local_income_tax_rate = Column(Float, nullable=False)  # 지방소득세 비율

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    tax_brackets = relationship("TaxBracket", back_populates="salary_bracket")


class TaxBracket(Base):
    __tablename__ = "tax_brackets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    salary_bracket_id = Column(
        Integer, ForeignKey("salary_brackets.id"), nullable=False
    )
    lower_limit = Column(Float, nullable=False)  # 구간 하한
    upper_limit = Column(Float, nullable=True)  # 구간 상한 (최고 구간은 null)
    tax_rate = Column(Float, nullable=False)  # 세율
    deduction = Column(Float, nullable=False)  # 누진공제액

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    salary_bracket = relationship("SalaryBracket", back_populates="tax_brackets")


class SalaryBracketResponse(BaseModel):
    id: int
    year: int
    minimum_hourly_rate: float
    minimum_monthly_rate: float

    national_pension: float
    health_insurance: float
    employment_insurance: float
    long_term_care_insurance: float

    minimum_pension_income: float
    maximum_pension_income: float
    maximum_national_pension: float
    minimum_health_insurance: float
    maximum_health_insurance: float

    local_income_tax_rate: float
    tax_brackets: list["TaxBracketResponse"]


class SalaryBracketCreate(BaseModel):
    minimum_hourly_rate: float
    minimum_monthly_rate: float
    national_pension: float
    health_insurance: float
    employment_insurance: float
    long_term_care_insurance: float
    minimum_pension_income: float
    maximum_pension_income: float
    maximum_national_pension: float
    minimum_health_insurance: float
    maximum_health_insurance: float
    local_income_tax_rate: float
    tax_brackets: list["TaxBracketCreate"]

    @field_validator(
        "local_income_tax_rate",
        "health_insurance",
        "employment_insurance",
        "long_term_care_insurance",
    )
    def validate_rate(cls, v):
        if v < 0 or v > 100:
            raise ValueError("비율은 항상 0부터 100입니다.")
        return v


class TaxBracketResponse(BaseModel):
    id: int
    salary_bracket_id: int
    lower_limit: float
    upper_limit: float
    tax_rate: float
    deduction: float


class TaxBracketCreate(BaseModel):
    lower_limit: float
    upper_limit: float
    tax_rate: float
    deduction: float

    @field_validator("tax_rate")
    def validate_rate(cls, v):
        if v < 0 or v > 100:
            raise ValueError("비율은 항상 0부터 100입니다.")
        return v
