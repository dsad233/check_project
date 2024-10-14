from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Index,
    Float
)
from sqlalchemy.orm import relationship

from app.core.database import Base

# 급여 테이블 #
# 예를 들어 1000만원이 어떻게 나눠지는가에 대한 값이므로, 직접 설정하는 값이 아닙니다.
# 고정된 값들이 들어가게 됩니다.
class SalaryBracket(Base):
    __tablename__ = "salary_brackets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False) # 연도
    minimum_hourly_rate = Column(Integer, nullable=False) # 최저 시급
    minimum_monthly_rate = Column(Integer, nullable=False) # 최저 월급
    
    national_pension = Column(Integer, nullable=False) # 국민연금
    health_insurance = Column(Integer, nullable=False) # 건강보험
    employment_insurance = Column(Integer, nullable=False) # 고용보험
    long_term_care_insurance = Column(Integer, nullable=False) # 장기요양보험
    
    minimun_pension_income = Column(Integer, nullable=False) # 연금소득 최저
    maximum_pension_income = Column(Integer, nullable=False) # 연금소득 최대
    maximum_national_pension = Column(Integer, nullable=False) # 국민연금 최대
    minimum_health_insurance = Column(Integer, nullable=False) # 건강보험 최저
    maximum_health_insurance = Column(Integer, nullable=False) # 건강보험 최대
    
    local_income_tax_rate = Column(Float, nullable=False) # 지방소득세 비율
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    tax_brackets = relationship("TaxBracket", back_populates="salary_bracket")

class TaxBracket(Base):
    __tablename__ = "tax_brackets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    salary_bracket_id = Column(Integer, ForeignKey("salary_brackets.id"), nullable=False)
    lower_limit = Column(Integer, nullable=False) # 구간 하한
    upper_limit = Column(Integer, nullable=True) # 구간 상한 (최고 구간은 null)
    tax_rate = Column(Float, nullable=False) # 세율
    deduction = Column(Integer, nullable=False) # 누진공제액

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    salary_bracket = relationship("SalaryBracket", back_populates="tax_brackets")