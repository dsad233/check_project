from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Time,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.core.database import Base

# 해당 지점 권한 policies는 MSO, 최고관리자 한정이니, 다른 관리자급에 대해서는 고민할 필요 없음.
class BranchPolicies(Base): # 지점 설정 전체를 아우르는 테이블
    __tablename__ = "branch_policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")


#________________________________________________________________________________________#
# 근무설정 관련 테이블
class PartPolicies(Base): #파트 기본설정
    __tablename__ = "part_policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    branch_policy_id = Column(Integer, ForeignKey("branch_policies.id"), nullable=False)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    policy_details = Column(String(500), nullable=True)
    structure = Column(String(255), nullable=True)
    group = Column(String(255), nullable=True)
    auto_calculation = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    branch = relationship("Branches", back_populates="part_policies")
    branch_policy = relationship("BranchPolicies", back_populates="part_policies")
    part = relationship("Parts", back_populates="part_policies")

class CommutePolicies(Base): #출퇴근 설정 (출퇴근 사용여부 설정 / IP 출퇴근 사용여부 설정도 있으나, 순위는 후순위니 참고만)
    __tablename__ = "commute_policies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    branch_policy_id = Column(Integer, ForeignKey("branch_policies.id"), nullable=False)
    do_commute = Column(Boolean, default=False)
    allowed_ip_commute = Column(String(255), nullable=True) # 여러 아이피 주소를 쉼표로 구분해서 저장
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    branch = relationship("Branches", back_populates="commute_policies")
    branch_policy = relationship("BranchPolicies", back_populates="commute_policies")

class OverTimePolicies(Base): #연장근무 설정
    __tablename__ = "overtime_policies"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    branch_policy_id = Column(Integer, ForeignKey("branch_policies.id"), nullable=False)
    name = Column(String(255), nullable=False)  # 예: 의사, 간호사...
    
    # 연장근무 당 지급 금액 설정
    ot_30 = Column(Integer, nullable=False)
    ot_60 = Column(Integer, nullable=False)
    ot_90 = Column(Integer, nullable=False)
    ot_120 = Column(Integer, nullable=False)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    branch = relationship("Branches", back_populates="overtime_policies")
    branch_policy = relationship("BranchPolicies", back_populates="overtime_policies")

class AutoOvertimePolicies(Base):
    __tablename__ = "auto_overtime_policies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    branch_policy_id = Column(Integer, ForeignKey("branch_policies.id"), nullable=False)
    role = Column(
        Enum("최고관리자", "관리자", name="user_role"),
        nullable=False
    )
    is_auto_applied = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    branch = relationship("Branches", back_populates="auto_overtime_policies")
    branch_policy = relationship("BranchPolicies", back_populates="auto_overtime_policies")

class HolidayWorkPolicies(Base): #휴일근무 설정
    __tablename__ = "holiday_work_policies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    branch_policy_id = Column(Integer, ForeignKey("branch_policies.id"), nullable=False)
    do_holiday_work = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    branch = relationship("Branches", back_populates="holiday_work_policies")
    branch_policy = relationship("BranchPolicies", back_populates="holiday_work_policies")

class WeekendWorkPolicies(Base): #휴일근무 설정
    __tablename__ = "weekend_work_policies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    branch_policy_id = Column(Integer, ForeignKey("branch_policies.id"), nullable=False)
    do_weekend_work = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    branch = relationship("Branches", back_populates="holiday_work_policies")
    branch_policy = relationship("BranchPolicies", back_populates="holiday_work_policies")

class WorkPolicies(Base): #근로기본 설정
    __tablename__ = "work_policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    branch_policy_id = Column(Integer, ForeignKey("branch_policies.id"), nullable=False)
    weekly_work_days = Column(Integer, nullable=False)  # 주 근무일수
    
    # 평일 설정
    weekday_start_time = Column(Time, nullable=False)
    weekday_end_time = Column(Time, nullable=False)
    weekday_is_holiday = Column(Boolean, default=False)
    
    # 토요일 설정
    saturday_start_time = Column(Time, nullable=True)
    saturday_end_time = Column(Time, nullable=True)
    saturday_is_holiday = Column(Boolean, default=True)
    
    # 일요일 설정
    sunday_start_time = Column(Time, nullable=True)
    sunday_end_time = Column(Time, nullable=True)
    sunday_is_holiday = Column(Boolean, default=True)
    
    # 의사 휴게시간
    doctor_break_start_time = Column(Time, nullable=True)
    doctor_break_end_time = Column(Time, nullable=True)
    
    # 일반 직원 휴게시간
    staff_break_start_time = Column(Time, nullable=True)
    staff_break_end_time = Column(Time, nullable=True)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    branch = relationship("Branches", back_populates="work_policies")
    branch_policy = relationship("BranchPolicies", back_populates="work_policies")

class AllowancePolicies(Base):
    __tablename__ = "allowance_policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    branch_policy_id = Column(Integer, ForeignKey("branch_policies.id"), nullable=False)

    
    comprehensive_overtime = Column(Boolean, default=False) # 포괄산정 연장근무수당
    annual_leave = Column(Boolean, default=False) # 연차수당
    holiday_work = Column(Boolean, default=False) # 휴일수당
    job_duty = Column(Boolean, default=False) # 직무수당
    meal = Column(Boolean, default=False) # 식대

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    branch = relationship("Branches", back_populates="allowance_policies")
    branch_policy = relationship("BranchPolicies", back_populates="allowance_policies")

#________________________________________________________________________________________#
#________________________________________________________________________________________#
# 임금 설정 관련 테이블
# !! 대부분 직접 설정하는 게 아닌 앞서 설정한 기본설정 및 연봉 계산기를 통해서 자동으로 계산되는 부분들임에 유의 !!
class SalaryPolicies(Base):
    __tablename__ = "salary_policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    branch_policy_id = Column(Integer, ForeignKey("branch_policies.id"), nullable=False)
    base_salary = Column(Integer, nullable=False)
    meal_allowance = Column(Integer, nullable=True)
    position_allowance = Column(Integer, nullable=True)
    job_allowance = Column(Integer, nullable=True)
    overtime_allowance = Column(Integer, nullable=True)
    night_work_allowance = Column(Integer, nullable=True)
    holiday_work_allowance = Column(Integer, nullable=True)
    payment_day = Column(Integer, nullable=True)
    calculation_method = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    branch = relationship("Branches", back_populates="salary_policies")
    branch_policy = relationship("BranchPolicies", back_populates="salary_policies")
    part_salary_policies = relationship(
        "PartSalaryPolicies", back_populates="salary_policy"
    )

#________________________________________________________________________________________#
#________________________________________________________________________________________#
# 시급 설정 관련 테이블 #
class HourlyWagePolicies(Base):
    __tablename__ = "hourly_wage_policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    branch_policy_id = Column(Integer, ForeignKey("branch_policies.id"), nullable=False)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    
    work_start_time = Column(Time, nullable=False)
    work_end_time = Column(Time, nullable=False)
    break_time = Column(Integer, nullable=False)  # 휴게시간 (분 단위)
    hourly_wage = Column(Integer, nullable=False)  # 기본 시급
    
    additional_hourly_wage = Column(Integer, nullable=True)  # 추가 시급 (있는 경우)
    overtime_rate = Column(Float, nullable=True)  # 연장근무 할증률
    night_work_rate = Column(Float, nullable=True)  # 야간근무 할증률
    holiday_work_rate = Column(Float, nullable=True)  # 휴일근무 할증률
    
    is_common = Column(Boolean, default=False)  # 공통 정책 여부
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    branch = relationship("Branches", back_populates="hourly_wage_policies")
    branch_policy = relationship("BranchPolicies", back_populates="hourly_wage_policies")
    part = relationship("Parts", back_populates="hourly_wage_policies")

#________________________________________________________________________________________#
#________________________________________________________________________________________#
# 문서 설정 관련 테이블 #
class DocumentPolicies(Base):
    __tablename__ = "document_policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    branch_policy_id = Column(Integer, ForeignKey("branch_policies.id"), nullable=False)
    document_type = Column(String(255), nullable=False)
    can_view = Column(Boolean, default=False)
    can_edit = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")

    branch = relationship("Branches", back_populates="document_policies")
    branch_policy = relationship("BranchPolicies", back_populates="document_policies")

#________________________________________________________________________________________#
#________________________________________________________________________________________#
# 급여 테이블 #
# 예를 들어 1000만원이 어떻게 나눠지는가에 대한 값이므로, 직접 설정하는 값이 아닙니다.
# 고정된 값들이 들어가게 됩니다.
class SalaryBracket(Base):
    __tablename__ = "salary_brackets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    base_salary = Column(Integer, nullable=False)
    monthly_salary = Column(Integer, nullable=False)
    daily_rate = Column(Integer, nullable=False)
    hourly_rate = Column(Integer, nullable=False)
    meal_allowance = Column(Integer, nullable=False)
    national_pension = Column(Integer, nullable=False)
    health_insurance = Column(Integer, nullable=False)
    employment_insurance = Column(Integer, nullable=False)
    income_tax = Column(Integer, nullable=False)
    local_income_tax = Column(Integer, nullable=False)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)