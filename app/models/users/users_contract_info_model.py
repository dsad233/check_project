from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, Date, String, DateTime, Enum

from app.core.database import Base
from app.enums.common import YesNo
from app.enums.user_management import ContractType
from app.enums.users import EmploymentStatus


class ContractInfo(Base):
    __tablename__ = "contract_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 직원
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 담당 매니저
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)  # 파트

    hire_date = Column(Date, nullable=False)  # 입사일
    resignation_date = Column(Date, nullable=True)  # 퇴사일
    contract_renewal_date = Column(Date, nullable=True)  # 계약 갱신일

    job_title = Column(String(255), nullable=False)  # 직무
    position = Column(String(255), nullable=False)  #  직위
    employ_status = Column(
        Enum(*[e.value for e in EmploymentStatus], name="employ_status"),
        nullable=False,
        default=EmploymentStatus.PERMANENT
    )  # 고용 상태 (정규직, 계약직)
    activate_yn = Column(
        Enum(*[e.value for e in YesNo], name="activate_yn"),
        nullable=False,
        datetime=YesNo.YES
    )

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")  # Y인 경우 삭제 회원으로 분류

