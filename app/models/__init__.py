from app.core.database import Base
from sqlalchemy.orm import relationship

# models.py에서 정의된 모델들
from .models import Branches, Parts, Users

# policies/branchpolicies.py에서 정의된 모델들
from .policies.branchpolicies import (
    BranchPolicies, PartPolicies, CommutePolicies, OverTimePolicies,
    AutoOvertimePolicies, HolidayWorkPolicies, WeekendWorkPolicies,
    WorkPolicies, AllowancePolicies, SalaryPolicies, HourlyWagePolicies,
    DocumentPolicies, SalaryBracket
)

# policies/partpolicies.py에서 정의된 모델들
from .policies.partpolicies import PartWorkPolicies, PartSalaryPolicies

# 여기서 관계를 설정합니다
Branches.branch_policies = relationship("BranchPolicies", back_populates="branch")
Branches.part_policies = relationship("PartPolicies", back_populates="branch")
Branches.commute_policies = relationship("CommutePolicies", back_populates="branch")
Branches.overtime_policies = relationship("OverTimePolicies", back_populates="branch")
Branches.auto_overtime_policies = relationship("AutoOvertimePolicies", back_populates="branch")
Branches.holiday_work_policies = relationship("HolidayWorkPolicies", back_populates="branch")
Branches.weekend_work_policies = relationship("WeekendWorkPolicies", back_populates="branch")
Branches.work_policies = relationship("WorkPolicies", back_populates="branch")
Branches.allowance_policies = relationship("AllowancePolicies", back_populates="branch")
Branches.salary_policies = relationship("SalaryPolicies", back_populates="branch")
Branches.hourly_wage_policies = relationship("HourlyWagePolicies", back_populates="branch")
Branches.document_policies = relationship("DocumentPolicies", back_populates="branch")
Branches.salary_brackets = relationship("SalaryBracket", back_populates="branch")
Branches.users = relationship("Users", back_populates="branch")
Branches.parts = relationship("Parts", back_populates="branch")

Parts.part_policies = relationship("PartPolicies", back_populates="part")
Parts.hourly_wage_policies = relationship("HourlyWagePolicies", back_populates="part")
Parts.users = relationship("Users", back_populates="part")
Parts.branch = relationship("Branches", back_populates="parts")
Parts.part_work_policies = relationship("PartWorkPolicies", back_populates="part")
Parts.part_salary_policies = relationship("PartSalaryPolicies", back_populates="part")

Users.part = relationship("Parts", back_populates="users")
Users.branch = relationship("Branches", back_populates="users")

BranchPolicies.branch = relationship("Branches", back_populates="branch_policies")
BranchPolicies.part_policies = relationship("PartPolicies", back_populates="branch_policy")
BranchPolicies.commute_policies = relationship("CommutePolicies", back_populates="branch_policy")
BranchPolicies.overtime_policies = relationship("OverTimePolicies", back_populates="branch_policy")
BranchPolicies.auto_overtime_policies = relationship("AutoOvertimePolicies", back_populates="branch_policy")
BranchPolicies.holiday_work_policies = relationship("HolidayWorkPolicies", back_populates="branch_policy")
BranchPolicies.weekend_work_policies = relationship("WeekendWorkPolicies", back_populates="branch_policy")
BranchPolicies.work_policies = relationship("WorkPolicies", back_populates="branch_policy")
BranchPolicies.allowance_policies = relationship("AllowancePolicies", back_populates="branch_policy")
BranchPolicies.salary_policies = relationship("SalaryPolicies", back_populates="branch_policy")
BranchPolicies.hourly_wage_policies = relationship("HourlyWagePolicies", back_populates="branch_policy")
BranchPolicies.document_policies = relationship("DocumentPolicies", back_populates="branch_policy")
BranchPolicies.salary_brackets = relationship("SalaryBracket", back_populates="branch_policy")

WorkPolicies.part_work_policies = relationship("PartWorkPolicies", back_populates="work_policy")
SalaryPolicies.part_salary_policies = relationship("PartSalaryPolicies", back_populates="salary_policy")

PartWorkPolicies.part = relationship("Parts", back_populates="part_work_policies")
PartWorkPolicies.work_policy = relationship("WorkPolicies", back_populates="part_work_policies")
PartWorkPolicies.branch = relationship("Branches", back_populates="part_work_policies")

PartSalaryPolicies.part = relationship("Parts", back_populates="part_salary_policies")
PartSalaryPolicies.salary_policy = relationship("SalaryPolicies", back_populates="part_salary_policies")
PartSalaryPolicies.branch = relationship("Branches", back_populates="part_salary_policies")
