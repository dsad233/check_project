from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, Date, DateTime, String

from app.core.database import Base


class SalaryContract(Base):
    __tablename__ = "salary_contract"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    contract_start_date = Column(Date, nullable=False) # 계약 시작일
    contract_end_date = Column(Date, nullable=True) # 계약 종료일

    annual_salary = Column(Integer, nullable=False) # 연봉
    monthly_salary = Column(Integer, nullable=False) # 월급

    # ================== 과세 -------------------
    # 기본급
    base_salary = Column(Integer, nullable=False) # 기본급
    base_hour_per_week = Column(Integer, nullable=False) # 기본근무시간 (일주일)
    base_hour_per_day = Column(Integer, nullable=False) # 기본근무시간 (하루)

    # 포괄 산정 연장 근로 수당
    fixed_overtime_allowance = Column(Integer, nullable=False) # 고정연장근로수당
    fixed_overtime_hours = Column(Integer, nullable=False)  # 고정연장근로시간

    # 연차 수당
    annual_leave_allowance = Column(Integer, nullable=False) # 연차수당
    annual_leave_hour_per_day = Column(Integer, nullable=False) # 연차시간 (일)
    annual_leave_count = Column(Integer, nullable=False) # 연차수

    # 휴일 수당
    holiday_allowance = Column(Integer, nullable=True) # 휴일수당
    holiday_allowance_hours = Column(Integer, nullable=False) # 휴일수당시간

    # 직무 수당
    duty_allowance = Column(Integer, nullable=True) # 근무수당

    # 야간 수당
    night_allowance = Column(Integer, nullable=True) # 야간수당

    # ================== 비과세 -------------------
    # 식대
    meal_allowance = Column(Integer, nullable=True) # 식대

    # 차량 유지비
    vehicle_maintenance_allowance = Column(Integer, nullable=True) # 차량유지비

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")  # Y인 경우 삭제 회원으로 분류
